from lbnlp.models.load.matscholar_2020v1 import (
    load,
    NERClassifier,
)
import os
from elasticsearch import Elasticsearch
from elastic_transport import ObjectApiResponse
from dotenv import load_dotenv
from argparse import Namespace
import argparse
from typing import Optional

load_dotenv()
API_KEY: Optional[str] = os.getenv("API_KEY")

client: Elasticsearch = Elasticsearch(
    "https://localhost:9200", api_key=API_KEY, ca_certs="../../config/ca.crt"
)

program_name: str = """
add_papers.py
"""
program_usage: str = """
annotate_texts.py [options] -a AMT
"""
program_description: str = """description:
This is a python script to annotate existing files in elasticsearch
"""
program_epilog: str = """ 

"""
program_version: str = """
Version 1.0.0 2024-09-05
Created by Vikram Penumarti
"""


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
        "-a",
        "--amt",
        required=False,
        default=2000,
        type=int,
        help="[Optional] Number of documents to annotate",
    )
    parser.add_argument("-v", "--version", action="version", version=program_version)

    return parser


def get_abstracts(size) -> dict:
    query: dict = {
        "_source": ["id", "summary"],
        "query": {"bool": {"must_not": [{"exists": {"field": "properties"}}]}},
    }
    response: ObjectApiResponse = client.search(
        index="search-papers-meta", size=size, query=query
    )["hits"]["hits"]
    abstracts: dict = {}
    for res in response:
        id, abstract = res["_source"]["id"], res["_source"]["summary"]  # type: ignore
        abstracts[id] = abstract

    return abstracts


def perform_analysis(ner_model: NERClassifier, abstract: dict):
    tags = ner_model.tag_doc(abstract["summary"])

    return tags


def main(args) -> None:
    ner_model: NERClassifier = load("ner")
    abstracts: dict = get_abstracts(args.size)

    tags = [
        perform_analysis(ner_model, {abstract: abstracts[abstract]})
        for abstract in abstracts
    ]

    print(tags)


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
