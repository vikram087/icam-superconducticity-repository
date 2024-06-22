from transformers import BertForQuestionAnswering, BertTokenizer, logging, pipeline, Pipeline
# import torch
# import string
import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY: str = os.getenv('API_KEY')

# Initialize Elasticsearch client
client: Elasticsearch = Elasticsearch(
    "https://localhost:9200",
    api_key=API_KEY,
    ca_certs="../config/ca.crt"
)

# Fetch papers from Elasticsearch
papers: dict = client.search(query={"match_all": {}}, index="search-papers-meta", size=10)
abstracts: list[str] = [paper['_source']['summary'] for paper in papers['hits']['hits']]

# Load the BERT model and tokenizer for question answering
logging.set_verbosity_error()
model_name: str = "deepset/bert-large-uncased-whole-word-masking-squad2"
model: BertForQuestionAnswering = BertForQuestionAnswering.from_pretrained(model_name)
# model = "path/to/save/fine-tuned-model"
tokenizer: BertTokenizer = BertTokenizer.from_pretrained(model_name)

qa_pipeline: Pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

# Define questions
questions: list[str] = [
    "Is this paper theoretical, experimental, or computational?",
    "What phenomena or phase is discussed?",
    "What chemical formulas or constituents are mentioned?",
    "What is the lattice name or crystal structure?",
    "What specific properties, like transition temperature, are mentioned?",
    "What theoretical or computational techniques are used?",
    "What experimental characterization techniques are mentioned?",
    "What experimental techniques are used for crystal growth?",
    "Does the paper mention important applications?" # newly added (mostly not mentioned)
]

def main() -> None:
    for abstract in abstracts:
        print(f"Abstract: {abstract}\n")
        for question in questions:
            # answer = get_answer(question, abstract, model, tokenizer)
            answer: dict = qa_pipeline(question=question, context=abstract)
            print(f"Question: {question}\nAnswer: {answer['answer']}\nScore: {answer['score']}\n")
        print("\n")

if __name__ == "__main__":
    main()
    
# def get_answer(question, context, model, tokenizer):
#     inputs = tokenizer(question, context, return_tensors='pt', truncation=True, padding=True)
#     input_ids = inputs['input_ids'].tolist()[0]

#     outputs = model(**inputs)
#     answer_start = torch.argmax(outputs.start_logits)
#     answer_end = torch.argmax(outputs.end_logits) + 1

#     answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    
#     answer = answer.strip().replace("[CLS]", "").replace("[SEP]", "")
    
#     answer = standardize_answers(answer, question, context)
    
#     return answer

# def standardize_answers(answer, question, abstract):
#     if answer == "":
#         return "N/A"
    
#     # Function to clean text
#     def clean_text(text):
#         return text.translate(str.maketrans('', '', string.punctuation)).replace(" ", "").lower()

#     clean_answer = clean_text(answer)
#     clean_question = clean_text(question)
#     clean_abstract = clean_text(abstract)

#     # If the answer is essentially the question or the entire abstract, return 'N/A'
#     if clean_answer == clean_question or clean_answer == clean_abstract or not clean_answer:
#         return "N/A"
    
#     return answer