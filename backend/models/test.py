import argparse

program_name: str = """
test.py
"""
program_usage: str = """
test.py [options] --model-type TYPE
"""
program_description: str = """description:
This is a python script to annotate/classify scientific documents leveraging the 
matscholar, matbert, and relevance models
"""
program_epilog: str = """ 

"""
program_version: str = """
Version 1.0.0 2024-10-30
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
        "--model-type",
        required=True,
        type=str,
        help="""
        [Required] Model to use
        - matscholar: Lightweight, less accurate ner model
        - matbert: Heavy, more accurate model (what is currently used)
        - relevance: Relevance classification 0 (not relevant), 1 (relevant)
        """,
    )
    parser.add_argument("-v", "--version", action="version", version=program_version)

    return parser


def model_selection(model_type):
    if model_type == "matscholar":
        from lbnlp.models.load.matscholar_2020v1 import load

        ner_model = load("ner")
    elif model_type == "matbert":
        from lbnlp.models.load.matbert_ner_2021v1 import load

        ner_model = load("solid_state")
    elif model_type == "relevance":
        from lbnlp.models.load.relevance_2020v1 import load

        ner_model = load("relevance")

    return ner_model


def get_documents():
    doc = "© 2016 WILEY-VCH Verlag GmbH & Co. KGaA, Weinheim. There is much current interest in combining superconductivity and spin-orbit coupling in order to induce the topological superconductor phase and associated Majorana-like quasiparticles which hold great promise towards fault-tolerant quantum computing. Experimentally these effects have been combined by the proximity-coupling of super-conducting leads and high spin-orbit materials such as InSb and InAs, or by controlled Cu-doping of topological insu-lators such as Bi2Se3. However, for practical purposes, a single-phase material which intrinsically displays both these effects is highly desirable. Here we demonstrate coexisting superconducting correlations and spin-orbit coupling in molecular-beam-epitaxy-grown thin films of GeTe. The former is evidenced by a precipitous low-temperature drop in the electrical resistivity which is quelled by a magnetic field, and the latter manifests as a weak antilocalisation (WAL) cusp in the magnetotransport. Our studies reveal several other intriguing features such as the presence of two-dimensional rather than bulk transport channels below 2 K, possible signatures of topological superconductivity, and unexpected hysteresis in the magnetotransport. Our work demonstrates GeTe to be a potential host of topological SC and Majorana-like excitations, and to be a versatile platform to develop quantum information device architectures."
    return [doc]


def annotate(docs, model, model_type):
    if model_type == "matscholar":
        tags = [model.tag_doc(doc) for doc in docs]
    elif model_type == "matbert":
        tags = model.tag_docs(docs)
    elif model_type == "relevance":
        tags = model.classify_many(docs)

    return tags


def main(args):
    model_type = args.model_type

    model = model_selection(model_type)
    docs = get_documents()
    tags = annotate(docs, model, model_type)

    print(tags)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = set_parser(
        program_name,
        program_usage,
        program_description,
        program_epilog,
        program_version,
    )
    args = parser.parse_args()
    main(args)
