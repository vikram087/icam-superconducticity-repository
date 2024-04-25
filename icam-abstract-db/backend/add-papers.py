from bs4 import BeautifulSoup
import requests
import re
import json
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer
import time

load_dotenv()
API_KEY = os.getenv('API_KEY')

# client = Elasticsearch(
#   "https://localhost:9200",
#   api_key=API_KEY,
#   ssl_context=context,
# )

client = Elasticsearch("http://localhost:9200")

model = SentenceTransformer('all-MiniLM-L6-v2')

# print(client.info())

class Paper:
    def __init__(self, link: str, title: str, date: str, citation: str, summary: str, authors: str, doi: str, journal: str):
        self.link = link
        self.title = title
        self.date = date
        self.citation = citation
        self.summary = summary
        self.authors = authors
        self.doi = doi
        self.journal = journal
        
    def __init__(self):
        self.link = ''
        self.title = ''
        self.date = ''
        self.citation = ''
        self.summary = ''
        self.authors = ''
        self.doi = ''
        self.journal = ''
        
    def __str__(self):
        return f"link: {self.link}\ntitle: {self.title}\ndate: {self.date}\ncitation: {self.citation}\nabstract: {self.summary}\nauthors: {self.authors}\ndoi: {self.doi}\njournal: {self.journal}"        

def findInfo(page) -> list[Paper]:
    url = f"https://journals.aps.org/search/results?sort=recent&clauses=%5B%7B%22field%22:%22abstitle%22,%22value%22:%22superconductivity%22,%22operator%22:%22AND%22%7D%5D&page={page}&per_page=20"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.find_all("script")
    text = ''.join(str(element) for element in content) # possibly unnecessary, join just to split again
                                                        # consider omitting and just iterating through content
                                                        # then only keeping those which match html pattern

    extracted_texts = [part.strip() for part in text.split('"html"') if part.strip()]
    extracted_texts.pop(0)
        
    # pattern = r'html(.*?)html'
    # matches = re.finditer(pattern, text, re.DOTALL) # Issue is here "html" ... "html" ... "html" ... "html"
                                                    # Only gets the alternates, bc it searches after each tag
    
    # extracted_texts = [f"{match.group(1)}" for match in matches]
                
    return assignPaperMetadata(extracted_texts)

def assignPaperMetadata(extracted_texts: list[str]) -> list[Paper]:
    papers = []
    fields = ["link", "title", "date", "citation", "summary", "authors", "doi", "journal"]
    
    for extracted in extracted_texts:
        paper = Paper()
            
        for field in fields:
            patterns = rf'"{field}":"(.*?)(?=",")'
        
            matches = re.search(patterns, extracted)
            field1 = f'No {field} found'
            if(matches):
                field1 = f"{matches.group(1)}"
            
            if(field == "link"):
                field1 = "https://journals.aps.org/" + field1
                
            decoded_text = field1.encode().decode('unicode-escape').replace('\\"', '"')
                
            setattr(paper, field, decoded_text)
        
        exists = False
        for pub in papers:
            if(pub.title == paper.title):
                exists = True
                break
        if(not exists):
            papers.append(paper)
            
    return papers

"""
Below is all the stuff with embeddings for vectorized search
"""

def createNewIndex(delete):
    if client.indices.exists(index='search-papers') and delete:
        client.indices.delete(index='search-papers')
    if not client.indices.exists(index="search-papers"):
        client.indices.create(
            index="search-papers", 
            mappings={
                'properties': {
                    'embedding': {
                        'type': 'dense_vector',
                    },
                    # 'elser_embedding': {
                    #     'type': 'sparse_vector',
                    # },
                },
            },
            # settings={
            #     'index': {
            #         'default_pipeline': 'elser-ingest-pipeline'
            #     }
            # }
        )
    else:
        print("Index already exists and no deletion specified")
        

def getEmbedding(text):
    return model.encode(text)

def upload_documents(start, end):
    pages = range(start, end)
    all_papers = []
    
    for page in pages:
        papers = findInfo(page)
        for paper in papers:
            paper_dict = {
                "title": paper.title,
                "authors": paper.authors,
                "link": paper.link,
                "date": paper.date,
                "citation": paper.citation,
                "doi": paper.doi,
                "journal": paper.journal,
                "summary": paper.summary
            }
            all_papers.append(paper_dict)
        print(page)
        
    return all_papers  

def insert_documents(documents):
    operations = []
    for document in documents:
        operations.append({'create': {'_index': 'search-papers', "_id": document["doi"]} })
        operations.append({
            **document,
            "embedding": getEmbedding(document["summary"]),
        })
    return client.bulk(operations=operations)

createNewIndex(False)
insert_documents(upload_documents(1, 101))
# 1-101

"""
Code for adding specific categorical searches, 
category:superconductivity --> This uses superconductivity as a categorical search

def extract_filters(query):
    filters = []

    filter_regex = r'category:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'term': {
                'category.keyword': {
                    'value': m.group(1)
                }
            }
        })
        query = re.sub(filter_regex, '', query).strip()

    return {'filter': filters}, query
"""


"""
Old code for keyword search

def upload_all_papers(start, end):
    pages = range(start, end)
    all_papers = []
    ES = { "index" : { "_index" : "search-papers-meta" } }
    
    for page in pages:
        papers = findInfo(page)
        for paper in papers:
            action = {
                "create": {
                    "_index": "search-papers-meta",
                    "_id": paper.doi
                }
            }
            paper_dict = {
                "title": paper.title,
                "authors": paper.authors,
                "link": paper.link,
                "date": paper.date,
                "citation": paper.citation,
                "doi": paper.doi,
                "journal": paper.journal,
                "summary": paper.summary
            }    
            all_papers.append(json.dumps(action))
            all_papers.append(json.dumps(paper_dict))
        print(page)
        
    docs = '\n'.join(all_papers) + '\n'
        
    client.bulk(body=docs, pipeline="ent-search-generic-ingestion")
        
    results = client.search(index="search-papers-meta", q="supercon")
    hits = results['hits']['hits']
    papers = [hit['_source'] for hit in hits]
    print(papers[0]['summary'])
 
This code is what is used to add papers to DB
createIndex()
upload_all_papers(101, 201)
1-8
8-21
21-51
51-101
101-201
"""

"""
Do not have current capacity to use these

def deploy_elser():
    # download ELSER v2
    client.ml.put_trained_model(model_id='.elser_model_2',
                                    input={'field_names': ['text_field']})
    
    # wait until ready
    while True:
        status = client.ml.get_trained_models(model_id='.elser_model_2',
                                                include='definition_status')
        if status['trained_model_configs'][0]['fully_defined']:
            # model is ready
            break
        time.sleep(1)

    # deploy the model
    client.ml.start_trained_model_deployment(model_id='.elser_model_2')

    # define a pipeline
    client.ingest.put_pipeline(
        id='elser-ingest-pipeline',
        processors=[
            {
                'inference': {
                    'model_id': '.elser_model_2',
                    'input_output': [
                        {
                            'input_field': 'summary',
                            'output_field': 'elser_embedding',
                        }
                    ]
                }
            }
        ]
    )
    
def deploy_elser_model():
    try:
        deploy_elser()
    except Exception as exc:
        print(f'Error: {exc}')
    else:
        print(f'ELSER model deployed.')
"""