from transformers import BertForQuestionAnswering, BertTokenizer
import torch
import string

model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
model = BertForQuestionAnswering.from_pretrained(model_name)
tokenizer = BertTokenizer.from_pretrained(model_name)

abstract = "The superconducting high-entropy alloys (HEAs) recently attract considerable attention due to their exciting properties, such as the robustness of superconductivity against atomic disorder and extremely high-pressure. The well-studied crystal structure of superconducting HEAs is body-centered-cubic (bcc) containing Nb, Ti, and Zr atoms. The same elements are contained in Al5Nb24Ti40V5Zr26, which is a recently discovered bcc HEA and shows a gum-metal-like behavior after cold rolling. The gum metal is also an interesting system, exhibiting superelasticity and low Young's modulus. If gum metals show superconductivity and can be used as a superconducting wire, the gum-metal HEA superconductors might be the next-generation superconducting wire materials. Aiming at a fundamental assessment of as-cast Al-Nb-Ti-V-Zr multicomponent alloys including Al5Nb24Ti40V5Zr26, we have investigated the structural and superconducting properties of the alloys. All alloys investigated show the superconductivity, and the valence electron concentration dependence of the superconducting critical temperature is very close to those of typical superconducting bcc HEAs."

questions = [
    "Is this paper based on a theory, an experiment, or a computational study?",
    "What phenomena or general phase/property is discussed?",
    "Mention the chemical formulas or constituents.",
    "Describe the lattice name or crystal structure.",
    "List any specific properties mentioned, such as transition temperature.",
    "Which theoretical or computational techniques are used?",
    "What experimental techniques are used for characterization?",
    "What experimental techniques are used for crystal growth?"
]

def get_answer(question, context, model, tokenizer):
    inputs = tokenizer(question, context, return_tensors='pt', truncation=True, padding=True)
    input_ids = inputs['input_ids'].tolist()[0]

    outputs = model(**inputs)
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1

    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    
    # Remove special tokens and check if the answer is valid
    answer = answer.replace('[CLS]', '').replace('[SEP]', '').strip()
    if standardizeNames(answer) == standardizeNames(question) or not answer:
        answer = 'N/A'
    
    return answer

def standardizeNames(sentence):
    sentence.translate(str.maketrans('', '', string.punctuation))
    sentence = sentence.replace(" ", "")
    sentence = sentence.lower()
    return sentence

for question in questions:
    answer = get_answer(question, abstract, model, tokenizer)
    print(f"Question: {question}\nAnswer: {answer}\n")
