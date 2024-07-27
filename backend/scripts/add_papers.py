# from bs4 import BeautifulSoup
# import requests
import argparse
import os
import time
import urllib.request as libreq
from argparse import Namespace

import feedparser  # type: ignore
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from feedparser import FeedParserDict
from generate_data import generate_answers
from sentence_transformers import SentenceTransformer  # type: ignore

program_name: str = """
add_papers.py
"""
program_usage: str = """
add_papers.py [options] -i ITER -a AMT
"""
program_description: str = """description:
This is a python script to upload a specified number of documents to an elasticsearch
database from arXiv
"""
program_epilog: str = """ 

"""
program_version: str = """
Version 3.0 2024-06-01
Created by Vikram Penumarti
"""

load_dotenv()
API_KEY: str | None = os.getenv("API_KEY")

client: Elasticsearch = Elasticsearch(
    "https://localhost:9200", api_key=API_KEY, ca_certs="../config/ca.crt"
)

# print(client.info())
# exit()

# client = Elasticsearch("http://localhost:9200")

model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")


def set_parser(
    program_name: str,
    program_usage: str,
    program_description: str,
    program_epilog: str,
    program_version: str,
) -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=program_name,
        usage=program_usage,
        description=program_description,
        epilog=program_epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--iter",
        required=False,
        default=1,
        type=int,
        help="[Optional] Number of iterations of file uploads to perform (higher number is more likely to get rate limited, min 1)",
    )
    parser.add_argument(
        "-a",
        "--amt",
        required=False,
        default=2000,
        type=int,
        help="[Optional] Number of documents to fetch from arXiv (max 2000, min 1)",
    )
    parser.add_argument("-v", "--version", action="version", version=program_version)

    return parser


def findInfo(start: int, amount: int) -> list[dict]:
    search_query: str = "all:superconductivity"
    #   wait_time = 60

    url: str = f"http://export.arxiv.org/api/query?search_query={search_query}&start={start}&max_results={amount}"

    print(f"Searching arXiv for {search_query}")

    with libreq.urlopen(url) as response:
        content: bytes = response.read()

    feed: FeedParserDict = feedparser.parse(content)

    paper_list: list[dict] = []
    for entry in feed.entries:
        paper_dict: dict = {
            "id": entry.id.split("/abs/")[-1].replace("/", "-"),
            "title": entry.title,
            "links": [link["href"] for link in entry.get("links")],
            "summary": entry.get("summary"),
            "date": int(time.strftime("%Y%m%d", entry.get("published_parsed"))),
            "updated": int(time.strftime("%Y%m%d", entry.get("updated_parsed"))),
            "categories": [category["term"] for category in entry.get("tags")],
            "authors": [author["name"] for author in entry.get("authors")],
            "doi": entry.get("arxiv_doi"),
            "journal_ref": entry.get("arxiv_journal_ref"),
            "comments": entry.get("arxiv_comment"),
            "primary_category": entry.get("arxiv_primary_category").get("term"),
        }

        paper_list.append(paper_dict)

    print(f"Collected papers {start} - {start + amount}")

    #   print(f'Sleeping for {wait_time} seconds')
    #   time.sleep(wait_time)

    return replaceNullValues(paper_list)


def replaceNullValues(papers_list: list[dict]) -> list[dict]:
    for paper_dict in papers_list:
        for key, val in paper_dict.items():
            if not val:
                paper_dict[key] = "N/A"

    return papers_list


def createNewIndex(delete: bool, index: str) -> None:
    if client.indices.exists(index=index) and delete:
        client.indices.delete(index=index)
    if not client.indices.exists(index=index):
        client.indices.create(
            index=index,
            mappings={
                "properties": {
                    "embedding": {"type": "dense_vector"},
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


def getEmbedding(text: str) -> list[int]:
    return model.encode(text)


def insert_documents(documents: list[dict], index: str):
    print("Starting Insertion")
    operations: list[dict] = []
    for document in documents:
        operations.append({"create": {"_index": index, "_id": document["id"]}})
        operations.append(
            {
                **document,
                "summary_embedding": getEmbedding(document["summary"]),
                "title_embedding": getEmbedding(document["title"]),
                "inferences": generate_answers(
                    {"summary": document["summary"], "id": document["id"]}
                ),
            }
        )
        # print(operations[1])
        # break

    print("Successfully Completed Insertion")
    return client.bulk(operations=operations)


def upload_to_es(amount: int, iterations: int) -> None:
    wait_time: int = 3
    start: int = client.count(index="search-papers-meta")["count"]
    print(f"Total documents in DB, start: {start}\n")
    for i in range(iterations):
        insert_documents(findInfo(start, amount), "search-papers-meta")
        print(f"Uploaded documents {start} - {start + amount}")
        start += amount

        print(f"Sleeping for {wait_time} seconds")
        time.sleep(wait_time)

    print(f"Total documents in DB, finish: {start}\n")


def main(args: Namespace) -> None:
    amount: int = args.amt
    iterations: int = args.iter
    if amount > 2000 or amount < 1 or iterations < 1:
        raise Exception(
            "Flag error: please ensure your flag values match the specifications"
        )

    upload_to_es(amount, iterations)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = set_parser(
        program_name,
        program_usage,
        program_description,
        program_epilog,
        program_version,
    )
    args: Namespace = parser.parse_args()
    main(args)
