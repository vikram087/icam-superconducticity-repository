import json
import math
import os
from datetime import datetime
from typing import Mapping, Sequence

import redis
from dotenv import load_dotenv
from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from redis import Redis
from sentence_transformers import SentenceTransformer  # type: ignore

# import faiss

load_dotenv()
API_KEY: str | None = os.getenv("API_KEY")

client: Elasticsearch = Elasticsearch(
    "https://localhost:9200", api_key=API_KEY, ca_certs="../config/ca.crt"
)

# client = Elasticsearch("http://localhost:9200")

app: Flask = Flask(__name__)
CORS(app)
model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[int]:
    return model.encode(text)


# /api/papers/fetch
@app.route("/api/papers/fetch", methods=["POST"])
def get_papers() -> tuple[Response, int] | Response:
    data: dict = request.get_json()
    stars: list[str] = [key.replace("_", "-") for key in list(data.keys()) if data[key]]

    if len(stars) == 0:
        return jsonify(None)

    responses: list[ObjectApiResponse] = [
        client.get(index="search-papers-meta", id=star) for star in stars
    ]
    papers: list[dict] = [response["_source"] for response in responses]

    if papers:
        return jsonify(papers)
    else:
        return jsonify({"error": "No results found"}), 404


# /api/papers/${paperId}
@app.route("/api/papers/<paper_id>", methods=["GET"])
def get_paper(paper_id: str) -> tuple[Response, int] | Response:
    results: ObjectApiResponse = client.get(index="search-papers-meta", id=paper_id)
    paper: dict = results["_source"]
    if paper:
        return jsonify(paper)
    else:
        return jsonify({"error": "No results found"}), 404


redis_client: Redis = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


def get_cached_results(cache_key: str) -> dict | None:
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)  # type: ignore
    return None


def cache_results(cache_key: str, data: tuple[list[dict], int, dict]) -> None:
    redis_client.setex(cache_key, 3600, json.dumps(data))


def make_cache_key(
    query: str,
    sorting: str,
    page: int,
    num_results: int,
    pages: int,
    term: str,
    start_date: int,
    end_date: int,
    parsed_results: dict,
) -> str:
    key: str = f"{query}_{sorting}_{page}_{num_results}_{pages}_{term}_{start_date}_{end_date}_{parsed_results['must']}_{parsed_results['not']}_{parsed_results['or']}"
    return key


# cache.clear()
# print("Cleared cache")
# redis-cli FLUSHALL # command on cli to clear cache


# fuzzy search for category, authors
# vector-based search for title, summary
# /api/papers
@app.route("/api/papers", methods=["POST"])
def papers() -> tuple[Response, int] | Response:
    try:
        data: dict = request.get_json()
        page: int = int(data.get("page", 0))
        num_results: int = int(data.get("results", 0))
        query: str = str(data.get("query", ""))
        sorting: str = str(data.get("sorting", ""))
        pages: int = int(data.get("pages", 30))
        term: str = str(data.get("term", ""))
        parsed_input: dict = dict(data.get("parsedInput", []))

        print(parsed_input)
        print(query)

        must_v: list[str] = parsed_input["must"]
        or_v: list[str] = parsed_input["or"]
        not_v: list[str] = parsed_input["not"]

        today: datetime = datetime.today()
        formatted_date: str = today.strftime("%Y%m%d")
        date: str = str(data.get("date", f"00000000-{formatted_date}"))
        start_date: int = int(date.split("-")[0])
        end_date: int = int(date.split("-")[1])
    except Exception:
        return jsonify(None)

    if page < 0:
        return jsonify(None)
    if num_results < 0 or (
        num_results != 10
        and num_results != 20
        and num_results != 50
        and num_results != 100
    ):
        return jsonify(None)

    if term == "Abstract":
        field: str = "summary_embedding"
    elif term == "Title":
        field = "title_embedding"
    elif term == "Category":
        field = "categories"
    elif term == "Authors":
        field = "authors"
    else:
        return jsonify(None)

    cache_key: str = make_cache_key(
        query,
        sorting,
        page,
        num_results,
        pages,
        term,
        start_date,
        end_date,
        parsed_input,
    )
    cached: dict | None = get_cached_results(cache_key)
    if cached:
        return jsonify({"papers": cached[0], "total": cached[1], "accuracy": cached[2]})

    if sorting == "Most-Recent" or sorting == "Most-Relevant":
        sort: str = "desc"
    elif sorting == "Oldest-First":
        sort = "asc"
    else:
        return jsonify(None)

    knn_search: bool = False

    size: int = client.search(query={"match_all": {}}, index="search-papers-meta")[
        "hits"
    ]["total"]["value"]

    if pages < 1:
        return jsonify(None)
    elif pages * num_results > size:
        pages = math.ceil(size / num_results)

    k: int = page * num_results
    if k > size:
        k = size

    if sorting == "Most-Recent" or sorting == "Oldest-First":
        p_sort: Sequence[Mapping | str] = [{"date": {"order": sort}}, "_score"]
    elif sorting == "Most-Relevant":
        p_sort = [{"_score": {"order": sort}}]

    if query == "all" or field == "summary_embedding" or field == "title_embedding":
        tag = "summary" if field == "summary_embedding" else "title"
        must_clause = (
            [
                {"match": {tag: {"query": label, "fuzziness": "AUTO"}}}
                for label in must_v
            ]
            if must_v
            else {"match_all": {}}
        )
        should_clause = (
            [{"match": {tag: {"query": label, "fuzziness": "AUTO"}}} for label in or_v]
            if or_v
            else []
        )
        must_not_clause = (
            [{"match": {tag: {"query": label, "fuzziness": "AUTO"}}} for label in not_v]
            if not_v
            else []
        )
    else:
        must_clause = [{"match": {field: {"query": query, "fuzziness": "AUTO"}}}]

        if must_v:
            must_clause.extend(
                [
                    {"match": {field: {"query": label, "fuzziness": "AUTO"}}}
                    for label in must_v
                ]
            )

        should_clause = (
            [
                {"match": {field: {"query": label, "fuzziness": "AUTO"}}}
                for label in or_v
            ]
            if or_v
            else []
        )
        must_not_clause = (
            [
                {"match": {field: {"query": label, "fuzziness": "AUTO"}}}
                for label in not_v
            ]
            if not_v
            else []
        )

    quer = {
        "bool": {
            "must": must_clause,
            "should": should_clause,
            "must_not": must_not_clause,
            "filter": {
                "range": {
                    "date": {
                        "gte": start_date,
                        "lte": end_date,
                    }
                }
            },
        }
    }

    if query == "all" or field == "authors" or field == "categories":
        knn_search = False
        try:
            results: ObjectApiResponse = client.search(
                query=quer,
                size=num_results,
                from_=(page - 1) * num_results,
                sort=[{"date": {"order": sort}}]
                if (sorting == "Most-Recent" or sorting == "Oldest-First")
                else None,
                index="search-papers-meta",
            )
        except Exception:
            return jsonify(None)
        if results["hits"]["hits"] == []:
            return jsonify(None)

    elif field == "summary_embedding" or field == "title_embedding":
        knn_search = True
        try:
            results = client.search(
                knn={
                    "field": field,
                    "query_vector": get_embedding(query),
                    "num_candidates": size,
                    "k": k,
                },
                query=quer,
                from_=0,  # consider changing to (page-1)*num_results
                size=page * num_results,
                sort=p_sort,
                index="search-papers-meta",
            )
        except Exception:
            return jsonify(None)
        if results["hits"]["hits"] == []:
            return jsonify(None)

    hits: dict = results["hits"]["hits"]
    papers: list[dict] = []
    accuracy: dict = {}

    if not knn_search:
        for hit in hits:
            papers.append(hit["_source"])

    total: int = client.search(
        query=quer,
        size=num_results,
        from_=(page - 1) * num_results,
        sort=[{"date": {"order": sort}}],
        index="search-papers-meta",
    )["hits"]["total"]["value"]

    if total > num_results * pages:
        total = num_results * pages

    if knn_search:
        papers = hits[(page - 1) * num_results :]
        filtered_papers: list[dict] = [
            paper["_source"]
            for paper in papers
            if paper["_source"]["date"] > start_date
            and paper["_source"]["date"] < end_date
        ]
        for hit in hits:
            if not hit["_score"]:
                break
            accuracy[hit["_source"]["id"]] = float(str(hit["_score"])[1:])
    else:
        filtered_papers = list(papers)

    if filtered_papers:
        cache_results(cache_key, (filtered_papers, total, accuracy))

        return jsonify(
            {"papers": filtered_papers, "total": total, "accuracy": accuracy}
        )
    else:
        return jsonify({"error": "No results found"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=8080)
