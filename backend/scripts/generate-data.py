from openai import OpenAI
import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
API_KEY: str|None = os.getenv('API_KEY')

gpt: OpenAI = OpenAI()

# Initialize Elasticsearch client
client: Elasticsearch = Elasticsearch(
    "https://localhost:9200",
    api_key=API_KEY,
    ca_certs="../config/ca.crt"
)

def getAbstracts(index: str, size: int) -> list[str]:
    data: dict = client.search(index=index, size=size)['hits']['hits']
    abstracts: list[str] = [data[i]['_source']['summary'] for i in range(len(data))]
    
    return abstracts

## FIXME: Fix answer start locations
## FIXME: Prompt engineer further
def getTrainingData(abstracts: list[str]) -> dict:
    questions: list[str] = [
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
    
    system_message: dict = {"role": "system", "content": "You are a helpful assistant designed to output JSON."}
    responses: list[dict] = []
    
    for i in range(len(abstracts)):
        context_message: dict = {"role": "assistant", "content": f"Here is the abstract:\n\n{abstracts[i]}"}
        qas: list[dict] = []
        
        for j in range(len(questions)):
            messages: list[dict] = [
                system_message,
                context_message,
                {"role": "user", "content": questions[j]}
            ]
            response = gpt.chat.completions.create(
                model="gpt-4o",
                response_format={ "type": "json_object" },
                messages=messages # type: ignore
            )
            answer: str = response.choices[0].message.content
            
            qas.append({
                "id": f"{i}-{j}",
                "question": questions[j],
                "answers": [{
                    "text": answer,
                    "answer_start": abstracts[i].find(answer) if answer in abstracts[i] else -1
                }],
                "is_impossible": False
            })
            
        responses.append({
            "context": abstracts[i],
            "qas": qas
        })
        
    squad_format: dict = {
        "version": "v2.0",
        "data": [{
            "title": "Generated Abstracts",
            "paragraphs": responses
        }]
    }
                    
    return squad_format

## Further prompt engineer
def getInferences(abstracts: list[str]) -> list[dict]:
    questions: list[str] = [
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
    
    system_message: dict = {"role": "system", "content": "You are a helpful assistant whos goal is to answer the questions based off the context given in the abstract."}
    responses: list[dict] = []
    
    for i in range(len(abstracts)):
        context_message: dict = {"role": "assistant", "content": f"Here is the abstract:\n\n{abstracts[i]}"}
        for j in range(len(questions)):
            messages: list[dict] = [
                system_message,
                context_message,
                {"role": "user", "content": questions[j]}
            ]
            response = gpt.chat.completions.create(
                model="gpt-4o",
                response_format={ "type": "json_object" },
                messages=messages # type: ignore
            )
            answer: str|None = response.choices[0].message.content
            responses.append({"question": questions[j], "answer": answer})
            
    return responses
    
def main() -> None:
    abstracts: list[str] = getAbstracts("search-papers-meta", 1)
    
    ## For Training Data
    squad: dict = getTrainingData(abstracts)
    jason: str = json.dumps(squad, indent=4)
    print(jason)
    
    ## For inferences (choose to not fine-tune Bert)
    # inferences: list[dict] = getInferences(abstracts)
    # jason = json.dumps(inferences, indent=4)
    # print(jason)
    
if __name__ == "__main__":
    main()