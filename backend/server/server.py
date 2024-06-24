from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from elasticsearch import Elasticsearch
from elastic_transport import ObjectApiResponse
from dotenv import load_dotenv
import os
import json
from sentence_transformers import SentenceTransformer # type: ignore
import redis
from redis import Redis
import math
from datetime import datetime
from typing import Sequence, Mapping
# import faiss

load_dotenv()
API_KEY: str|None = os.getenv('API_KEY')

client: Elasticsearch = Elasticsearch(
  "https://localhost:9200",
  api_key=API_KEY,
  ca_certs="../config/ca.crt"
)

# client = Elasticsearch("http://localhost:9200")

app: Flask = Flask(__name__)
CORS(app)
model: SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')

def getEmbedding(text: str) -> list[int]:
    return model.encode(text)

# /api/papers/${paperId}
@app.route('/api/papers/<paper_id>', methods=['GET'])
def get_paper(paper_id: str) -> tuple[Response, int]|Response:
    results: ObjectApiResponse = client.get(index="search-papers-meta", id=paper_id)
    paper: dict = results['_source']
    if paper:
        return jsonify(paper)
    else:
        return jsonify({"error": "No results found"}), 404


redis_client: Redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def get_cached_results(cache_key: str) -> dict|None:
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data) # type: ignore
    return None

def cache_results(cache_key: str, data: tuple[list[dict], int, dict]) -> None:
    redis_client.setex(cache_key, 3600, json.dumps(data))
    
def make_cache_key(query: str, sorting: str, page: int, numResults: int, pages: int, term: str, startDate: int, endDate: int) -> str:
    key: str = f"{query}_{sorting}_{page}_{numResults}_{pages}_{term}_{startDate}_{endDate}"
    return key

# cache.clear()
# print("Cleared cache")
# redis-cli FLUSHALL # command on cli to clear cache

# fuzzy search for category, authors
# vector-based search for title, summary
# /api/papers
@app.route("/api/papers", methods=['POST'])
def papers() -> tuple[Response, int]|Response:
    data: dict = request.get_json()
    page: int = int(data.get('page', 0))
    numResults: int = int(data.get('results', 0))
    query: str = str(data.get('query', ""))
    sorting: str = str(data.get('sorting', ""))
    pages: int = int(data.get('pages', 30))
    term: str = str(data.get('term', ""))
    
    today: datetime = datetime.today()
    formatted_date: str = today.strftime('%Y%m%d')
    date: str = str(data.get('date', f"00000000-{formatted_date}"))
    startDate: int = int(date.split("-")[0])
    endDate: int = int(date.split("-")[1])
    
    if term == "Abstract":
        field: str = "summary_embedding"
    elif term == "Title":
        field = "title_embedding"
    elif term == "Category":
        field = "categories"
    elif term == "Authors":
        field = "authors"
        
    cache_key: str = make_cache_key(query, sorting, page, numResults, pages, term, startDate, endDate)
    cached: dict|None = get_cached_results(cache_key)
    if cached:
        return jsonify({ "papers": cached[0], "total": cached[1], "accuracy": cached[2] })

    if(sorting == "Most-Recent" or sorting == "Most-Relevant"):
        sort: str = "desc"
    elif(sorting == "Oldest-First"):
        sort = "asc"
        
    knnSearch: bool = False
    
    size: int = client.search(query={"match_all": {}}, index="search-papers-meta")['hits']['total']['value']
    
    if pages < 1:
        pages = 1
    elif pages*numResults > size:
        pages = math.ceil(size/numResults)
        
    k: int = page*numResults
    if k > size:
        k = size
    
    if sorting == "Most-Recent" or sorting == "Oldest-First":
        pSort: Sequence[Mapping|str] = [{"date": {"order": sort}}, "_score"]
    elif sorting == "Most-Relevant":
        pSort = [{'_score': {'order': sort}}]
        
    if query == "all" or field == "summary_embedding" or field == "title_embedding":
        quer: dict={
            "bool": {
                "must": {
                    "match_all": {}
                },
                "filter": {
                    "range": {
                        "date": {
                            "gte": startDate,
                            "lte": endDate,
                        }
                    }
                }
            }
        }
    else:
        quer={
            "bool": {
                "must": {
                    "match": {
                        field: {
                            "query": query,
                            "fuzziness": "AUTO"
                        }
                    }
                },
                "filter": {
                    "range": {
                        "date": {
                            "gte": startDate,
                            "lte": endDate,
                        }
                    }
                }
            }
        }
        
    if query == "all" or field == "authors" or field == "categories":
        knnSearch = False
        results: ObjectApiResponse = client.search(
            query=quer,
            size=numResults,
            from_=(page-1)*numResults,
            sort=[{"date": {"order": sort}}] if (sorting == "Most-Recent" or sorting == "Oldest-First") else None,
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
            query=quer,
            from_=0,
            size=page*numResults,
            sort=pSort,
            index="search-papers-meta"
        )
        
    hits: dict = results['hits']['hits']
    papers: list[dict] = []
    accuracy: dict = {}
    
    if not knnSearch:
        for hit in hits:
            papers.append(hit['_source'])

    total: int = client.search(
            query=quer,
            size=numResults,
            from_=(page-1)*numResults,
            sort=[{"date": {"order": sort}}],
            index="search-papers-meta"
        )['hits']['total']['value']
    
    if total > numResults*pages:
        total = numResults*pages
    
    if knnSearch:
        papers = hits[(page-1)*numResults:]
        filtered_papers: list[dict] = [paper['_source'] for paper in papers if paper['_source']['date'] > startDate and paper['_source']['date'] < endDate]
        for hit in hits:
            if not hit['_score']:
                break
            accuracy[hit['_source']['id']] = float(str(hit['_score'])[1:])
    else:
        filtered_papers = list(papers)
            
    if filtered_papers:
        cache_results(cache_key, ( filtered_papers, total, accuracy ))

        return jsonify({ "papers": filtered_papers, "total": total, "accuracy": accuracy })
    else:
        return jsonify({"error": "No results found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=8080)