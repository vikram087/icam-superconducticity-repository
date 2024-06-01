from flask import Flask, jsonify, request
from flask_cors import CORS
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import json
from sentence_transformers import SentenceTransformer
import redis
import math
# import faiss

load_dotenv()
API_KEY = os.getenv('API_KEY')

client = Elasticsearch(
  "https://localhost:9200",
  api_key=API_KEY,
  ca_certs="./ca.crt"
)

# client = Elasticsearch("http://localhost:9200")

app = Flask(__name__)
CORS(app)
model = SentenceTransformer('all-MiniLM-L6-v2')

def getEmbedding(text):
    return model.encode(text)

# /api/papers/${paperId}
@app.route('/api/papers/<paper_id>', methods=['GET'])
def get_paper(paper_id):
    results = client.get(index="search-papers-meta", id=paper_id)
    paper = results['_source']
    if paper:
        return jsonify(paper)
    else:
        return jsonify({"error": "No results found"}), 404


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
# cache = TTLCache(maxsize=100, ttl=3600)
def get_cached_results(cache_key):
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    return None

def cache_results(cache_key, data):
    redis_client.setex(cache_key, 3600, json.dumps(data))
    
def make_cache_key(query, sorting, page, numResults, pages, term):
    key = f"{query}_{sorting}_{page}_{numResults}_{pages}_{term}"
    return key

# cache.clear()
# print("Cleared cache")
# redis-cli FLUSHALL # command on cli to clear cache

# fuzzy search for category, authors
# vector-based search for title, summary
# /api/papers
@app.route("/api/papers", methods=['POST'])
def papers():
    data = request.get_json()
    page = int(data.get('page', 0))
    numResults = int(data.get('results', 0))
    query = str(data.get('query', ""))
    sorting = str(data.get('sorting', ""))
    pages = int(data.get('pages', 30))
    term = str(data.get('term', ""))
    
    if term == "Abstract":
        field = "summary_embedding"
    elif term == "Title":
        field = "title_embedding"
    elif term == "Category":
        field = "categories"
    elif term == "Authors":
        field = "authors"
        
    cache_key = make_cache_key(query, sorting, page, numResults, pages, term)
    cached = get_cached_results(cache_key)
    if cached:
        return jsonify({ "papers": cached[0], "total": cached[1], "accuracy": cached[2] })

    if(sorting == "Most-Recent" or sorting == "Most-Relevant"):
        sort = "desc"
    elif(sorting == "Oldest-First"):
        sort = "asc"
        
    knnSearch = False
    
    size = client.search(query={"match_all": {}}, index="search-papers-meta")['hits']['total']['value']
    
    if pages < 1:
        pages = 1
    elif pages*numResults > size:
        pages = math.ceil(size/numResults)
        
    k = page*numResults
    if k > size:
        k = size
    
    if sorting == "Most-Recent" or sorting == "Oldest-First":
        pSort = [{"date": {"order": sort}}, "_score"]
    elif sorting == "Most-Relevant":
        pSort = [{'_score': {'order': sort}}]
        
    if query == "all":
        results = client.search(
            query={"match_all": {}},
            size=numResults,
            from_=(page-1)*numResults,
            sort=[{"date": {"order": sort}}],
            index="search-papers-meta"
        )
    elif field == "summary_embedding" or field == "title_embedding":
        knnSearch = True
        results = client.search(
            knn={
                'field': field,
                'query_vector': getEmbedding(query),
                'num_candidates': size,
                'k': k,
            },
            # size=numResults,
            # from_=(page-1)*numResults,
            from_=0,
            size=page*numResults,
            sort=pSort,
            index="search-papers-meta"
        )
    elif field == "authors" or field == "categories":
        knnSearch = False
        results = client.search(
            query = {
                "match": {
                    field: {
                        "query": query,
                        "fuzziness": "AUTO"
                    }
                }
            },
            index="search-papers-meta",
        )
        
    hits = results['hits']['hits']
    papers = []
    accuracy = {}
    
    if not knnSearch:
        for i in range(len(hits)):
            papers.append(hits[i]['_source'])
    
    total = numResults*pages
    if total > size:
        total = size
    
    if knnSearch:
        papers = hits[(page-1)*numResults:]
        # filtered_papers = [hit['_source'] for hit in papers]
        filtered_papers = [papers[i]['_source'] for i in range(len(papers))]
        for i in range(len(hits)):
            if not hits[i]['_score']:
                break
            accuracy[hits[i]['_source']['id']] = hits[i]['_score']
    else:
        filtered_papers = list(papers)
        if results['hits']['total']['value'] < total:
            total = results['hits']['total']['value']
            
    if filtered_papers:
        cache_results(cache_key, ( filtered_papers, total, accuracy ))

        return jsonify({ "papers": filtered_papers, "total": total, "accuracy": accuracy })
    else:
        return jsonify({"error": "No results found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=8080)