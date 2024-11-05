import argparse
import logging
import os
import time
import urllib.request as libreq
from argparse import Namespace
from typing import Optional

import feedparser  # type: ignore
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from feedparser import FeedParserDict
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
Higher values for amount and iterations are more likely to be rate limited
"""
program_version: str = """
Version 2.3.1 2024-06-01
Created by Vikram Penumarti
"""

load_dotenv()
API_KEY: Optional[str] = os.getenv("API_KEY")
ES_URL: Optional[str] = os.getenv("ES_URL")
LBNLP_URL: str | None = os.getenv("LBNLP_URL")

client: Elasticsearch = Elasticsearch(ES_URL, api_key=API_KEY, ca_certs="./ca.crt")

logging.basicConfig(level=logging.INFO)

# logging.info(client.info())
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
        default=40,
        type=int,
        help="[Optional] Number of iterations of file uploads to perform (min 1)\nDefault: 40",
    )
    parser.add_argument(
        "-a",
        "--amt",
        required=False,
        default=50,
        type=int,
        help="[Optional] Number of documents to fetch from arXiv (max 2000, min 1)\nDefault: 50",
    )
    parser.add_argument("-v", "--version", action="version", version=program_version)

    return parser


def findInfo(start: int, amount: int) -> tuple[list[dict], bool]:
    search_query: str = "all:superconductivity"
    paper_list: list[dict] = []

    i = 0
    while True:
        url: str = f"http://export.arxiv.org/api/query?search_query={search_query}&start={start}&max_results={amount}"

        logging.info(f"Searching arXiv for {search_query}")

        try:
            with libreq.urlopen(url) as response:
                content = response.read()
        except Exception as e:
            logging.info(f"Error fetching data from arXiv: {e}")
            exit()

        feed: FeedParserDict = feedparser.parse(content)

        if len(feed.entries) == 0:
            if i == 4:
                logging.info(
                    "Something is wrong, you've been rate limited 5 times in a row, take some time before you run this script again\nConsider increasing wait time, decreasing amount of papers fetched, or adjusting query"
                )
                logging.info("Exiting program")
                exit()

            logging.info("You've been rate limited 💀💀\nSleeping for 300 seconds")
            time.sleep(300)
            i += 1
            continue

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

            bad = client.options(ignore_status=[404]).get(
                index="search-papers-meta", id=paper_dict["id"]
            )
            exists = bad.get("found")
            if exists is True:
                return paper_list, True

            paper_list.append(paper_dict)

        logging.info(f"Collected papers {start} - {start + amount}")
        return replaceNullValues(paper_list), False


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
        logging.info("Index already exists and no deletion specified")


def getEmbedding(text: str) -> list[int]:
    return model.encode(text)


def insert_documents(documents: list[dict], index: str):
    logging.info("Starting Insertion")
    operations: list[dict] = []
    for document in documents:
        operations.append({"create": {"_index": index, "_id": document["id"]}})
        operations.append(
            {
                **document,
                "summary_embedding": getEmbedding(document["summary"]),
                "title_embedding": getEmbedding(document["title"]),
            }
        )
        # logging.info(operations[1])
        # break

    logging.info("Successfully Completed Insertion")
    return client.bulk(operations=operations)


def upload_to_es(amount: int, iterations: int) -> None:
    wait_time: int = 10
    start: int = client.count(index="search-papers-meta")["count"]
    logging.info(f"Total documents in DB, start: {start}\n")
    for _ in range(iterations):
        docs, ex = findInfo(start, amount)
        insert_documents(docs, "search-papers-meta")
        logging.info(f"Uploaded documents {start} - {start + amount}")
        start += amount

        if ex:
            logging.info(f"Total documents in DB, finish: {start}\n")
            logging.info("Database is fully updated, exiting")
            exit()

        logging.info(f"Sleeping for {wait_time} seconds")
        time.sleep(wait_time)

    logging.info(f"Total documents in DB, finish: {start}\n")


def main(args: Namespace) -> None:
    createNewIndex(False, "search-papers-meta")
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
