from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re
import json
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')

client = Elasticsearch(
  "https://d3e6ab8052bf4bc79ddc6e6682153d0e.us-central1.gcp.cloud.es.io:443",
  api_key=API_KEY
)

app = Flask(__name__)
CORS(app)

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

def upload_all_papers():
    limit = 626
    pages = range(1, limit)
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
        
    client.bulk(body='\n'.join(all_papers) + '\n', pipeline="ent-search-generic-ingestion")
    # results = client.search(index="search-papers-meta", q="supercon")
    # hits = results['hits']['hits']
    # papers = [hit['_source'] for hit in hits]
    # print(papers[0]['summary'])
    
@app.route('/api/results', methods=['POST'])
def get_results():
    data = request.get_json()
    query = str(data.get('query', ''))
    results = client.search(index="search-papers-meta", q=query)
    hits = results['hits']['hits']
    papers = [hit['_source'] for hit in hits]
    
    if papers:
        return jsonify(papers)
    else:
        return jsonify({"error": "No results found"}), 404

# /api/papers/${paperId}
@app.route('/api/papers/<paper_id>', methods=['GET'])
def get_paper(paper_id):
    doi = paper_id.replace("-", "/")

    results = client.get(index="search-papers-meta", id=doi)
    paper = results['_source']
    if paper:
        return jsonify(paper)
    else:
        return jsonify({"error": "No results found"}), 404

# /api/papers
@app.route("/api/papers", methods=['POST'])
def papers():
    data = request.get_json()
    page = int(data.get('page', 0))
    numResults = int(data.get('results', 0))
    query = str(data.get('query', ""))
    sorting = str(data.get('sorting', ""))

    if(sorting == "Most-Recent"):
        sort = "desc"
    elif(sorting == "Oldest-First"):
        sort = "asc"
    else:
        sort = ""
    
    if query == "all":
        results = client.search(
            index="search-papers-meta",
            body={
                "query": {
                    "match_all": {}
                },
                "sort": [
                    {"date": {"order": sort}}
                ],
                "size": numResults,
                "from": (page-1)*numResults
            }
        )
    else:
        results = client.search(
            index="search-papers-meta",
            body={
                "query": {
                    "match": {
                        "summary": query
                    }                
                },
                "sort": [
                    {"date": {"order": sort}}
                ],
                "size": numResults,
                "from": (page-1)*numResults
            }
        )
        
    hits = results['hits']['hits']
    papers = [hit['_source'] for hit in hits]
    total = results['hits']['total']['value']
    if papers:
        # return jsonify(papers)
        return jsonify({ "papers": papers, "total": total })
    else:
        return jsonify({"error": "No results found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=8080)