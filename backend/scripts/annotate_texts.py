from backend.lbnlp.lbnlp.models.load.matscholar_2020v1 import (
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


abstract = "© 2016 WILEY-VCH Verlag GmbH & Co. KGaA, Weinheim. There is much current interest in combining superconductivity and spin-orbit coupling in order to induce the topological superconductor phase and associated Majorana-like quasiparticles which hold great promise towards fault-tolerant quantum computing. Experimentally these effects have been combined by the proximity-coupling of super-conducting leads and high spin-orbit materials such as InSb and InAs, or by controlled Cu-doping of topological insu-lators such as Bi2Se3. However, for practical purposes, a single-phase material which intrinsically displays both these effects is highly desirable. Here we demonstrate coexisting superconducting correlations and spin-orbit coupling in molecular-beam-epitaxy-grown thin films of GeTe. The former is evidenced by a precipitous low-temperature drop in the electrical resistivity which is quelled by a magnetic field, and the latter manifests as a weak antilocalisation (WAL) cusp in the magnetotransport. Our studies reveal several other intriguing features such as the presence of two-dimensional rather than bulk transport channels below 2 K, possible signatures of topological superconductivity, and unexpected hysteresis in the magnetotransport. Our work demonstrates GeTe to be a potential host of topological SC and Majorana-like excitations, and to be a versatile platform to develop quantum information device architectures."

def main(args) -> None:
    ner_model: NERClassifier = load("ner")
 #   abstracts: dict = get_abstracts(args.size)

#    tags = [
#        perform_analysis(ner_model, {abstract: abstracts[abstract]})
#        for abstract in abstracts
#    ]
    tags = perform_analysis(ner_model, abstract) 

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
