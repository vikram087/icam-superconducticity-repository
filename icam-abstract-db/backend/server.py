from flask import Flask, jsonify, request
from flask_cors import CORS
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')

# client = Elasticsearch(
#   "https://d3e6ab8052bf4bc79ddc6e6682153d0e.us-central1.gcp.cloud.es.io:443",
#   api_key=API_KEY
# )

client = Elasticsearch(
  "http://localhost:9200")

app = Flask(__name__)
CORS(app)
    
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
    journals = str(data.get('journals', ""))
    
    journalArr = [] if journals == "None" else journals.split(',') # fails to return results

    if(sorting == "Most-Recent"):
        sort = "desc"
    elif(sorting == "Oldest-First"):
        sort = "asc"
    else:
        sort = ""
    
    base_query = {
        "size": numResults,
        "from": (page-1)*numResults,
        "sort": [{"date": {"order": sort}}]
    }

    if query == "all":
        base_query["query"] = {"match_all": {}}
    else:
        base_query["query"] = {"match": {"summary": query}}
        
    # if journalArr:
    #     base_query["query"] = {
    #         "bool": {
    #             "must": base_query["query"],
    #             "filter": { "terms":  {"journal": journalArr}}
    #         }
    #     }
        
    # base_query = {
    #     'size': 20, 
    #     'from': 0, 
    #     'sort': [{'date': {'order': 'desc'}}], 
    #     'query': {"match": {'journal': 'PRB'}} # journal needs to be of type keyword
    # }

    results = client.search(
        index="search-papers-meta",
        body=base_query
    )
        
    hits = results['hits']['hits']
    papers = [hit['_source'] for hit in hits]
    total = results['hits']['total']['value']
    
    # print(f"total: {total}\nbase query: {base_query}\njournals: {journalArr}")
        
    if papers:
        # return jsonify(papers)
        return jsonify({ "papers": papers, "total": total })
    else:
        return jsonify({"error": "No results found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=8080)