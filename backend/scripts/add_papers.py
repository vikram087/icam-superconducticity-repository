import argparse
import logging
import math
import os
import subprocess
import time
import urllib.request as libreq
from argparse import Namespace

import feedparser  # type: ignore
import redis
import requests
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from feedparser import FeedParserDict
from redis import Redis
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
API_KEY: str | None = os.getenv("API_KEY")
ES_URL: str | None = os.getenv("ES_URL")
LBNLP_URL: str | None = os.getenv("LBNLP_URL")
DOCKER: str | None = os.getenv("DOCKER")
INDEX: str = os.getenv("INDEX") or ""

client: Elasticsearch = Elasticsearch(ES_URL, api_key=API_KEY, ca_certs="./ca.crt")

logging.basicConfig(level=logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("elastic_transport").setLevel(logging.WARNING)
logging.getLogger("root").setLevel(logging.INFO)

model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

redis_host = "redis" if DOCKER == "true" else "localhost"
redis_client: Redis = redis.StrictRedis(
    host=redis_host, port=6379, db=0, decode_responses=True
)


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
        help="[Optional] Number of iterations of document uploads to perform (min 1)\nDefault: 40",
    )
    parser.add_argument(
        "-a",
        "--amt",
        required=False,
        default=50,
        type=int,
        help="[Optional] Number of papers to fetch from arXiv (max 2000, min 1)\nDefault: 50",
    )
    parser.add_argument(
        "-f",
        "--flush-all",
        required=False,
        default=False,
        action="store_true",
        help="[Optional] Enabling flag flushes redis DB after papers added\nDefault: False",
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        required=False,
        default=50,
        type=int,
        help="[Optional] Batch size of documents to be annotated at once\nDefault: 50",
    )
    parser.add_argument(
        "-s",
        "--sleep-between-calls",
        type=int,
        required=False,
        default=15,
        help="[Optional] Sleep time (in seconds) between API calls to arXiv\nDefault: 15",
    )
    parser.add_argument(
        "-r",
        "--sleep-after-rate-limit",
        type=int,
        required=False,
        default=300,
        help="[Optional] Sleep time (in seconds) after hitting rate limit before making next API call\nDefault: 300",
    )
    parser.add_argument(
        "-d",
        "--drop-batches",
        required=False,
        default=False,
        action="store_true",
        help="[Optional] Enabling flag does not upload an iteration of papers if all the batches do not successfully complete\nDefault: False",
    )
    parser.add_argument(
        "--restart",
        required=False,
        default=False,
        action="store_true",
        help="[Optional] Enabling flag tries to restart the 'models' docker container upon connection failure\nDefault: False",
    )
    parser.add_argument("-v", "--version", action="version", version=program_version)

    return parser


def sleep_with_timer(seconds: int) -> None:
    for remaining in range(seconds, 0, -1):
        print(f"INFO:root:Resuming in {remaining} seconds...", end="\r", flush=True)
        time.sleep(1)
    logging.info("\nResuming now...")


def findInfo(
    start: int,
) -> tuple[list[dict], bool, bool]:
    search_query: str = "all:superconductivity"
    paper_list: list[dict] = []
    dups: int = 0

    i: int = 0
    while True:
        url: str = f"http://export.arxiv.org/api/query?search_query={search_query}&start={start}&max_results={amount}"

        logging.info(f"Searching arXiv for {search_query}")

        try:
            with libreq.urlopen(url) as response:
                content: bytes = response.read()
        except Exception as e:
            logging.error(f"Error fetching data from arXiv: {e}")
            exit()

        feed: FeedParserDict = feedparser.parse(content)

        if len(feed.entries) == 0:
            if i == 2:
                logging.error(
                    "Rate limited three times in a row. Consider increasing wait time or adjusting query."
                )
                logging.error("Exiting program")
                exit()

            logging.warning(
                f"Rate limited. Sleeping for {sleep_after_rate_limit} seconds"
            )
            sleep_with_timer(sleep_after_rate_limit)
            i += 1
            continue

        summaries: list[str] = []
        paper_dicts: list[dict] = []

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

            summaries.append(paper_dict["summary"])
            paper_dicts.append(paper_dict)

        num_batches: int = math.ceil(len(summaries) / batch_size)

        all_annotations: list[dict] = []
        interrupted: bool = False

        batch_num: int = 0
        subprocess_run: bool = False

        while batch_num < num_batches:
            batch_start: int = batch_num * batch_size
            batch_end: int = batch_start + batch_size

            batch_summaries: list[str] = summaries[batch_start:batch_end]
            batch_paper_dicts: list[dict] = paper_dicts[batch_start:batch_end]

            try:
                annotations_response: requests.Response = requests.post(
                    f"{LBNLP_URL}/api/annotate/matbert",
                    json={"docs": batch_summaries},
                    headers={"Content-Type": "application/json"},
                )
            except requests.exceptions.ConnectionError:
                if restart and not subprocess_run:
                    try:
                        logging.info("Attempting to restart 'models' docker container")
                        result = subprocess.run(
                            [
                                "docker",
                                "compose",
                                "-f",
                                "../../docker/docker-compose.yml",
                                "up",
                                "-d",
                                "--build",
                                "models",
                            ],
                            capture_output=True,
                            text=True,
                            check=True,
                        )

                        logging.info(result.stdout)
                        logging.error(result.stderr)

                        subprocess_run = True
                        logging.info(
                            "Sleeping for 15s to ensure container restarted successfully"
                        )
                        sleep_with_timer(30)
                        continue
                    except Exception:
                        logging.error(
                            "Subprocess failed to restart docker container, exiting"
                        )
                        exit()
                elif restart and subprocess_run:
                    logging.error(
                        "Docker container failed twice in same iteration, exiting"
                    )
                    exit()

                if not drop_batches and batch_size >= amount:
                    logging.error(
                        "Batch did not successfully complete and current payload is empty, exiting"
                    )
                    exit()

                elif not drop_batches:
                    interrupted = True
                    logging.warning(
                        "Batch did not successfully complete, uploading current documents"
                    )
                    break

                logging.error(
                    "Batch did not successfully complete, dropping all batches\nTo upload partial iterations, please enable the --drop-batches flag"
                )
                exit()

            if annotations_response.status_code == 200:
                logging.info(
                    f"Batch {batch_num + 1}/{num_batches} annotation succeeded"
                )
                batch_annotations = annotations_response.json().get("annotation", [])
            else:
                logging.error(
                    f"Batch {batch_num + 1}/{num_batches} annotation failed: "
                    f"{annotations_response.status_code}, {annotations_response.text}"
                )
                batch_annotations = [{}] * len(batch_paper_dicts)

            all_annotations.extend(batch_annotations)

            batch_num += 1

        for paper_dict, annotation in zip(paper_dicts, all_annotations):
            paper_dict["APL"] = annotation.get("APL", [])
            paper_dict["CMT"] = annotation.get("CMT", [])
            paper_dict["DSC"] = annotation.get("DSC", [])
            paper_dict["MAT"] = annotation.get("MAT", [])
            paper_dict["PRO"] = annotation.get("PRO", [])
            paper_dict["PVL"] = annotation.get("PVL", [])
            paper_dict["PUT"] = annotation.get("PUT", [])
            paper_dict["SMT"] = annotation.get("SMT", [])
            paper_dict["SPL"] = annotation.get("SPL", [])

            bad = client.options(ignore_status=[404]).get(
                index=INDEX, id=paper_dict["id"]
            )
            exists = bad.get("found")
            if exists is True:
                logging.info("Duplicate paper found")
                dups += 1
                continue

            paper_list.append(paper_dict)

        logging.info(f"Collected papers {start} - {start + amount - dups}")
        return replaceNullValues(paper_list), False, interrupted


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
            body={
                "mappings": {
                    "properties": {
                        "embedding": {"type": "dense_vector"},
                    },
                },
                "settings": {
                    "number_of_replicas": 0,
                },
            },
        )
    else:
        logging.info("Index already exists and no deletion specified")


def getEmbedding(text: str):  # type: ignore
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

    logging.info("Successfully Completed Insertion")
    return client.bulk(operations=operations)


def upload_to_es() -> None:
    start: int = client.count(index=INDEX)["count"]
    logging.info(f"Total documents in DB, start: {start}\n")

    for _ in range(iterations):
        docs, ex, interrupted = findInfo(start)
        if len(docs) == 0:
            logging.error("No docs to upload, exiting")
            exit()

        insert_documents(docs, INDEX)
        logging.info(f"Uploaded documents {start} - {start + amount}")
        start += amount

        if ex:
            logging.info(f"Total documents in DB, finish: {start}\n")
            logging.info("Database is fully updated, exiting")
            exit()

        logging.info(f"Sleeping for {sleep_between_calls} seconds")
        sleep_with_timer(sleep_between_calls)

        if interrupted:
            logging.warning("Exiting due to all batches not successfully completing")
            exit()

    logging.info(f"Total documents in DB, finish: {start}\n")


def main() -> None:
    createNewIndex(False, INDEX)

    if amount > 2000 or amount < 1 or iterations < 1:
        raise Exception(
            "Flag error: please ensure your flag values match the specifications"
        )

    upload_to_es()

    if flush_all is True:
        redis_client.flushall()
        logging.info("Redis DB cleared")


if __name__ == "__main__":
    parser: argparse.ArgumentParser = set_parser(
        program_name,
        program_usage,
        program_description,
        program_epilog,
        program_version,
    )
    args: Namespace = parser.parse_args()

    amount: int = args.amt
    iterations: int = args.iter
    batch_size: int = args.batch_size
    sleep_after_rate_limit: int = args.sleep_after_rate_limit
    sleep_between_calls: int = args.sleep_between_calls
    drop_batches: bool = args.drop_batches
    restart: bool = args.restart
    flush_all: bool = args.flush_all

    main()
