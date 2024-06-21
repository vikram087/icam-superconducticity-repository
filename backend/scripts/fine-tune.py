import json
from transformers import BertForQuestionAnswering, BertTokenizer, Trainer, TrainingArguments
from datasets import Dataset

# Load your dataset
train_file_path = '../data/train_dataset.json'
validation_file_path = '../data/validation_dataset.json'

# Load the model and tokenizer
model_name = "deepset/bert-large-uncased-whole-word-masking-squad2"
model = BertForQuestionAnswering.from_pretrained(model_name)
tokenizer = BertTokenizer.from_pretrained(model_name)

# Load the dataset
with open(train_file_path) as f:
    train_dataset = json.load(f)
with open(validation_file_path) as f:
    validation_dataset = json.load(f)

# Prepare the datasets
train_dataset = Dataset.from_dict(train_dataset)
validation_dataset = Dataset.from_dict(validation_dataset)

# Preprocess the data
def preprocess_function(examples):
    questions = [q.strip() for q in examples["question"]]
    inputs = tokenizer(
        questions,
        examples["context"],
        max_length=384,
        truncation="only_second",
        return_offsets_mapping=True,
        padding="max_length",
        return_tensors="pt"
    )

    offset_mapping = inputs.pop("offset_mapping")
    answers = examples["answers"]

    start_positions = []
    end_positions = []

    for i, answer in enumerate(answers):
        if len(answer["text"]) == 0:
            start_positions.append(0)
            end_positions.append(0)
        else:
            start_positions.append(inputs.char_to_token(i, answer["answer_start"]))
            end_positions.append(inputs.char_to_token(i, answer["answer_start"] + len(answer["text"]) - 1))

    inputs.update(
        {
            "start_positions": start_positions,
            "end_positions": end_positions,
        }
    )
    return inputs

train_dataset = train_dataset.map(preprocess_function, batched=True)
validation_dataset = validation_dataset.map(preprocess_function, batched=True)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=validation_dataset,
)

if __name__ == "__main__":
    # Train the model
    trainer.train()

    # Save the fine-tuned model
    trainer.save_model("../models/fine-tuned-bert-large")
    tokenizer.save_pretrained("../models/fine-tuned-bert-large")

    results = trainer.evaluate()
    print(results)
