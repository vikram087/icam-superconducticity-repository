from flask import Flask, jsonify, request
from flask_cors import CORS
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer
from cachetools import TTLCache

load_dotenv()
API_KEY = os.getenv('API_KEY')

# client = Elasticsearch(
#   "https://d3e6ab8052bf4bc79ddc6e6682153d0e.us-central1.gcp.cloud.es.io:443",
#   api_key=API_KEY
# )

client = Elasticsearch("http://localhost:9200")

app = Flask(__name__)
CORS(app)
model = SentenceTransformer('all-MiniLM-L6-v2')

def getEmbedding(text):
    return model.encode(text)

# /api/papers/${paperId}
@app.route('/api/papers/<paper_id>', methods=['GET'])
def get_paper(paper_id):
    doi = paper_id.replace("-", "/")

    results = client.get(index="search-papers", id=doi)
    paper = results['_source']
    if paper:
        return jsonify(paper)
    else:
        return jsonify({"error": "No results found"}), 404


cache = TTLCache(maxsize=100, ttl=3600)
def get_cached_results(cache_key):
    return cache.get(cache_key)

def cache_results(cache_key, data):
    cache[cache_key] = data
    
def make_cache_key(query, sorting, page, numResults):
    key = f"{query}_{sorting}_{page}_{numResults}"
    return key

# cache.clear()
# print("Cleared cache")

# /api/papers
@app.route("/api/papers", methods=['POST'])
def papers():
    data = request.get_json()
    page = int(data.get('page', 0))
    numResults = int(data.get('results', 0))
    query = str(data.get('query', ""))
    sorting = str(data.get('sorting', ""))
    journals = str(data.get('journals', ""))
    
    cache_key = make_cache_key(query, sorting, page, numResults)
    cached = get_cached_results(cache_key)
    if cached:
        return jsonify({ "papers": cached[0], "total": cached[1], "accuracy": cached[2] })
    
    journalArr = [] if journals == "None" else journals.split(',') # fails to return results

    if(sorting == "Most-Recent" or sorting == "Most-Relevant"):
        sort = "desc"
    elif(sorting == "Oldest-First"):
        sort = "asc"
        
    knnSearch = False
        
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
    
    size = client.search(query={"match_all": {}}, index="search-papers")['hits']['total']['value']
        
    if query == "all":
        results = client.search(
            query={"match_all": {}},
            size=numResults,
            from_=(page-1)*numResults,
            sort=[{"date": {"order": sort}}],
            index="search-papers"
        )
    else:
        knnSearch = True
        if (sorting == "Most-Recent") or (sorting == "Oldest-First"):
            results = client.search(
                knn={
                    'field': 'embedding',
                    'query_vector': getEmbedding(query),
                    'num_candidates': size,
                    'k': size,
                },
                # size=numResults,
                # from_=(page-1)*numResults,
                from_=0,
                size=size,
                sort=[{"date": {"order": sort}}, "_score"],
                index="search-papers"
            )
        elif sorting == "Most-Relevant":
            results = client.search(
                knn={
                    'field': 'embedding',
                    'query_vector': getEmbedding(query),
                    'num_candidates': size,
                    'k': size,
                },
                # size=numResults,
                # from_=(page-1)*numResults,
                from_=0,
                size=size,
                sort=[{'_score': {'order': sort}}],
                index="search-papers"
            )
    #     results = client.search(
    #     query={
    #         'text_expansion': {
    #             'elser_embedding': {
    #                 'model_id': '.elser_model_2',
    #                 'model_text': query,
    #             }
    #         },
    #     },
    #     size=numResults,
    #     from_=(page-1)*numResults,
    #     index="search-papers"
    # )
        
    hits = results['hits']['hits']
    papers = []
    accuracy = {}
    
    if not knnSearch:
        papers = [hit['_source'] for hit in hits]
    
    for hit in hits:
        if not knnSearch or not hit['_score']:
            break
        if hit['_score'] >= 0.6:
            papers.append(hit['_source'])
            accuracy[hit['_source']['doi']] = hit['_score']
            
    # total = results['hits']['total']['value']
    filtered_papers = list(papers)
    if knnSearch:
        filtered_papers = papers[numResults*(page-1):numResults*page]
        total = len(papers)
    else:
        total = results['hits']['total']['value']
    
    # print(f"total: {total}\nbase query: {base_query}\njournals: {journalArr}")
        
    if papers:
        # return jsonify(papers)
        cache_results(cache_key, ( filtered_papers, total, accuracy ))
        return jsonify({ "papers": filtered_papers, "total": total, "accuracy": accuracy })
    else:
        return jsonify({"error": "No results found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=8080)