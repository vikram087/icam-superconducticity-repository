from transformers import LlamaForCausalLM, LlamaTokenizer # type: ignore
from dotenv import load_dotenv
import os
from elasticsearch import Elasticsearch
from elastic_transport import ObjectApiResponse
import torch
import argparse
from argparse import Namespace

program_name: str = """
generate_data.py
"""
program_usage: str = """
generate_data.py [options] -a AMT
"""
program_description: str = """description:
This is a python script to generate inferences for a specified number of documents in an elasticsearch
database
"""
program_epilog: str = """ 

"""
program_version: str = """
Version 1.0 2024-07-05
Created by Vikram Penumarti
"""

model_path: str = "../models/llama3-main/Meta-Llama-3-8B-Instruct/consolidated.00.pth"
tokenizer_path: str = "../models/llama3-main/Meta-Llama-3-8B-Instruct/tokenizer.model"

tokenizer: LlamaTokenizer = LlamaTokenizer.from_pretrained(tokenizer_path)
model: LlamaForCausalLM = LlamaForCausalLM.from_pretrained(model_path)

load_dotenv()
API_KEY: str|None = os.getenv('API_KEY')

client: Elasticsearch = Elasticsearch(
  "https://localhost:9200",
  api_key=API_KEY,
  ca_certs="../config/ca.crt"
)

def set_parser(program_name:str,program_usage:str,program_description:str,program_epilog:str,program_version:str) -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(prog=program_name,
                                     usage=program_usage,
                                     description=program_description,
                                     epilog=program_epilog,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-a','--amt', required=False, default=2000, type=int,
                        help="[Optional] Number of documents to generate inferences for")
    parser.add_argument('-v','--version', action='version', version=program_version)
    
    return parser

def define_questions() -> list[str]:
    return [
        "Is this paper theoretical, experimental, or computational?",
        "What phenomena or phase is discussed?",
        "What chemical formulas or constituents are mentioned?",
        "What is the lattice name or crystal structure?",
        "What specific properties, like transition temperature, are mentioned?",
        "What theoretical or computational techniques are used?",
        "What experimental characterization techniques are mentioned?",
        "What experimental techniques are used for crystal growth?",
        "Does the paper mention important applications?"
    ]

def get_abstracts(size: int) -> list[dict]:
    papers: ObjectApiResponse = client.search(
        query={
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "inferences"
                    }
                }
            }
        },
        index="search-papers-meta", 
        size=size
    )
    
    abstracts: list[dict] = []
    for paper in papers['hits']['hits']:
        summary: str = paper['_source']['summary']
        id: str = paper['_source']['id']
        
        abstracts.append({"summary": summary, "id": id})
    
    return abstracts

def generate_answers(abstract: dict) -> tuple[list[dict], str]:
    questions: list[str] = define_questions()
    answers = []
    
    for question in questions:
        prompt = f"Context: {abstract['summary']}\n\nQuestion: {question}\nAnswer:"
        
        inputs = tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=150)
        
        answers.append({"question": question, "answer": tokenizer.decode(output[0], skip_special_tokens=True)})
        
    return answers, abstract['id']

def input_to_db(answers: list[dict], id: str) -> None:
    client.update(
        index="search-papers-meta",
        id=id,
        doc={
            "inferences": answers
        }
    )

def main(args: Namespace) -> None:
    size: int = args.amt
    
    abstracts: list[dict] = get_abstracts(size)
    for abstract in abstracts:
        answers, id = generate_answers(abstract)
        input_to_db(answers, id)

if __name__ == "__main__":
    parser: argparse.ArgumentParser = set_parser(program_name,program_usage,program_description,program_epilog,program_version)
    args: Namespace = parser.parse_args()
    main(args)