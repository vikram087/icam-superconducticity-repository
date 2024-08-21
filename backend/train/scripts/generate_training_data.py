from openai import OpenAI
import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import math
from difflib import SequenceMatcher
import re
import argparse
from argparse import Namespace

program_name: str = """
generate_training_data.py
"""
program_usage: str = """
generate_training_data.py [options] -a AMT
"""
program_description: str = """description:
This is a python script to create training data for spacy based off of chatgpt
"""
program_epilog: str = """ 

"""
program_version: str = """
Version 1.0.0 2024-08-20
Created by Vikram Penumarti
"""

# Load environment variables
load_dotenv()
API_KEY: str | None = os.getenv("API_KEY")

gpt: OpenAI = OpenAI()

# Initialize Elasticsearch client
client: Elasticsearch = Elasticsearch(
    "https://localhost:9200", api_key=API_KEY, ca_certs="../../config/ca.crt"
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
        "-a",
        "--amt",
        required=False,
        default=500,
        type=int,
        help="[Optional] Number of documents to use for training/testing (max 500, min 1)\nDefault: 500",
    )
    parser.add_argument("-v", "--version", action="version", version=program_version)

    return parser


def get_abstracts(index: str, size: int) -> list[str]:
    data: dict = client.search(index=index, size=size)["hits"]["hits"]
    abstracts: list[str] = [summary["_source"]["summary"] for summary in data]

    return abstracts


def get_training_data(abstracts: list[str]) -> list[tuple]:
    prompt_template = """
    Generate annotations for the following characteristics using only text from the abstract provided by the assistant. Provide no extra text besides the annotations. Do not include the abstract in your answer. 
    Entities to be annotated include:
    - INORGANIC_MATERIAL
    - PROPERTY
    - APPLICATION
    - PHASE_LABEL
    - SAMPLE_DESCRIPTOR
    - SYNTHESIS_METHOD
    - CHARACTERIZATION_METHOD
    
    Example format:
    "The magnetic susceptibility of YBCO-123 superconductors shows a sharp transition at the critical temperature. This property is crucial for developing sensitive magnetic sensors used in medical imaging.",
    INORGANIC_MATERIAL: YBCO-123 superconductors
    APPLICATION: developing sensitive magnetic sensors used in medical imaging
    """

    system_message: dict = {
        "role": "system",
        "content": "You are a helpful assistant designed to output JSON.",
    }

    answers: list[tuple] = []
    for abstract in abstracts:
        context_message: dict = {
            "role": "assistant",
            "content": f"Abstract:\n\n{abstract}",
        }

        messages: list[dict] = [
            system_message,
            context_message,
            {"role": "user", "content": prompt_template},
        ]
        response = gpt.chat.completions.create(
            model="gpt-4o",
            messages=messages,  # type: ignore
        )
        answer: str | None = response.choices[0].message.content
        if answer:
            answer = answer.replace('"', "").replace("'", "")

        tup: tuple = (abstract, answer)
        answers.append(tup)

    return answers


def find_fuzzy_substring_indices(
    main_string: str, substring: str
) -> tuple[int, int] | tuple[None, None]:
    # Initialize variables to track the best match
    best_start: int = -1
    best_end: int = -1
    highest_ratio: float = 0.0

    # Iterate over the main_string to find the best match
    for i in range(len(main_string) - len(substring) + 1):
        # Extract a slice of the main_string of the same length as the substring
        candidate: str = main_string[i : i + len(substring)]

        # Check if the candidate is a full word match
        if re.match(
            r"\b" + re.escape(candidate) + r"\b", main_string[i : i + len(candidate)]
        ):
            # Calculate the similarity ratio
            ratio: float = SequenceMatcher(None, candidate, substring).ratio()

            # If the similarity ratio is higher than the previous best, update the best match
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_start = i
                best_end = i + len(substring) - 1

    if best_start != 0 and main_string[best_start - 1] != " ":
        # print("before:", main_string[best_start : best_end + 1])
        closest_space_before: int = main_string.rfind(" ", 0, best_start)

        if closest_space_before != -1:
            best_start = closest_space_before + 1
        else:
            best_start = 0

        # print("after:", main_string[best_start : best_end + 1])

    if best_end + 1 != len(main_string) and main_string[best_end + 1] != " ":
        # print("before:", main_string[best_start : best_end + 1])
        closest_space_after: int = main_string.find(" ", best_end + 1)

        if closest_space_after != -1:
            best_end = closest_space_after - 1
        else:
            best_end = len(main_string) - 1

        if not main_string[best_end].isalnum() and main_string[best_end] not in (
            ")",
            "]",
            "$",
        ):
            best_end -= 1

    # If no good match is found, return None
    if highest_ratio < 0.6:  # Adjust threshold as needed
        return None, None

    return best_start, best_end


def parse_answer(answers: list[tuple]) -> tuple[list[tuple], list[tuple]]:
    parsed: list[tuple] = []
    failed: list[tuple] = []
    i: int = 0

    for answer in answers:
        abstract: str = answer[0].strip().replace("\n", " ")
        annotations: list[str] = answer[1].split("\n")[1:]
        pair: dict = {"entities": []}

        for annotation in annotations:
            i += 1

            annotation = annotation.strip()
            value: str | None = None
            key: str | None = None

            try:
                key, value = annotation.split(":")
                value = value.strip()

                start, end = find_fuzzy_substring_indices(abstract, value)

                if not start or not end:
                    raise ValueError("String indexing error.")

                val: tuple[int, int, str] = (start, end, key.strip())
                pair["entities"].append(val)
            except ValueError as _:
                if value and key:
                    if value in abstract:
                        start, end = find_fuzzy_substring_indices(abstract, value)

                        if (not start or not end) and start != 0:
                            continue

                        pair["entities"].append((start, end, key.strip()))

                        print(
                            f"fixed on second try: abstract {math.ceil(i / len(answers))}, tag {math.ceil(i / len(annotations))}"
                        )
                        continue

                failed.append((abstract, key, value, annotation))
                continue

        parsed_answer: tuple[str, dict] = (abstract, pair)
        parsed.append(parsed_answer)

    return parsed, failed


# TRAIN_DATA = [
#     (
#         "The critical temperature of YBCO is 93 K.",
#         {"entities": [(27, 31, "PROPERTY"), (32, 36, "INORGANIC_MATERIAL")]},
#     ),
# ]


def write_to_training_file(train_data: list[tuple], test_data: list[tuple]) -> None:
    data: dict = {"../data/train.json": train_data, "../data/dev.json": test_data}

    for k, v in data.items():
        with open(k, "w") as file:
            file.write(str(v))


def get_parsed_data(amount) -> tuple[list, list]:
    abstracts: list[str] = get_abstracts("search-papers-meta", 2 * amount)

    train = abstracts[0:amount]
    test = abstracts[amount:]

    train_answers: list[tuple] = get_training_data(train)
    test_answers: list[tuple] = get_training_data(test)

    train_tags, train_failed = parse_answer(train_answers)
    test_tags, test_failed = parse_answer(test_answers)

    parsed_data = [train_tags, test_tags]
    fails = [train_failed, test_failed]

    return parsed_data, fails


def print_results(parsed_tags: list[tuple], failed: list[tuple]) -> None:
    for tags in parsed_tags:
        print("================================================\n")
        print(f"Abstract:\n\n{tags[0]}\n")
        print("Tags:\n")
        for entity in tags[1]["entities"]:
            print(entity)
            start: int = entity[0]
            end: int = entity[1]

            if (not start or not end) and start != 0:  # 0 evaluates to false
                print("Start or end not found")
                continue

            print(f"{tags[0][start:end+1]}\n")
        print("================================================\n")

    print("Failed:\n")
    count: int = 0
    for fail in failed:
        if fail[3] != "":
            if fail[1] or fail[2]:
                print(f"{fail}\n")
            elif not fail[1] and not fail[2]:
                print("GPT error, no val or key\n")

            continue
        count += 1

    sum_passed: int = 0
    for tags in parsed_tags:
        sum_passed += len(tags[1]["entities"])

    entity_tags: list[str] = [
        "INORGANIC_MATERIAL",
        "PROPERTY",
        "APPLICATION",
        "PHASE_LABEL",
        "SAMPLE_DESCRIPTOR",
        "SYNTHESIS_METHOD",
        "CHARACTERIZATION_METHOD",
    ]

    property_fail: int = 0
    for fail in failed:
        for en in entity_tags:
            if en in fail[3].split(":")[0]:
                property_fail += 1

    total_fail: int = len(failed) - count
    gpt_fail: int = total_fail - property_fail

    total_responses: int = total_fail + sum_passed

    accuracy: dict = {
        "Total Success": total_fail,
        "Parse Success": property_fail,
        "GPT Success": gpt_fail,
    }

    for name, fail in accuracy.items():
        percentage: float = 1 - fail / total_responses  # type: ignore
        percentage_string: str = f"{total_responses - fail}/{(total_responses)}"  # type: ignore

        print(f"Accuracy of run, {name}:\n{percentage*100}%\n{percentage_string}\n")


def main(args: Namespace) -> None:
    amount: int = args.amt

    parsed_data, fails = get_parsed_data(amount)
    write_to_training_file(parsed_data[0], parsed_data[1])

    print_results(parsed_data[0], fails[0])
    print_results(parsed_data[1], fails[1])


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
