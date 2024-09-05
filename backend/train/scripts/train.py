import spacy
from spacy.tokens import DocBin
from spacy.language import Language
from spacy.pipeline import EntityRecognizer
from spacy.tokens import Doc
import ast
import subprocess
from spacy.tokens import Span
from subprocess import CompletedProcess


def load_model() -> Language:
    nlp: Language = spacy.load("en_core_web_trf")

    # Add new labels to the NER component
    ner: EntityRecognizer = nlp.get_pipe("ner")

    labels: list[str] = [
        "INORGANIC_MATERIAL",
        "PROPERTY",
        "APPLICATION",
        "PHASE_LABEL",
        "SAMPLE_DESCRIPTOR",
        "SYNTHESIS_METHOD",
        "CHARACTERIZATION_METHOD",
    ]
    for label in labels:
        ner.add_label(label)

    return nlp


def load_train_data() -> list[tuple]:
    with open("../data/train.json", "r") as file:
        return ast.literal_eval(file.read())


def load_dev_data() -> list[tuple]:
    with open("../data/dev.json", "r") as file:
        return ast.literal_eval(file.read())


# def data_to_binary(nlp: Language, data: list[tuple]) -> None:
#     db = DocBin()

#     for text, annot in data:
#         doc: Doc = nlp.make_doc(text)
#         ents: list[Span] = []
#         for start, end, label in annot["entities"]:
#             span: Span | None = doc.char_span(
#                 start, end, label=label, alignment_mode="contract"
#             )
#             if span is None:
#                 print(f"Skipping entity {start, end, label}")
#             else:
#                 ents.append(span)
#         doc.ents = ents
#         db.add(doc)


#     db.to_disk("../data/train.spacy")
def data_to_binary(nlp: Language, data: list[tuple]) -> list[int]:
    db = DocBin()
    skipped: list[int] = [0, 0]

    for i, (text, annot) in enumerate(data):
        doc: Doc = nlp.make_doc(text)
        ents: list[Span] = []
        overlap_found = False
        for start, end, label in annot["entities"]:
            span: Span | None = doc.char_span(
                start, end, label=label, alignment_mode="contract"
            )
            if span is None:
                print(f"Skipping entity {start, end, label} in document {i}")
                skipped[0] += 1
            else:
                for ent in ents:
                    # Check if the current span overlaps with any existing span
                    if span.start < ent.end and span.end > ent.start:
                        overlap_found = True
                        print(
                            f"Overlap detected in document {i}: {span} overlaps with {ent}"
                        )
                        skipped[1] += 1
                # ents.append(span)
                if not overlap_found:
                    ents.append(span)

        doc.ents = ents
        db.add(doc)

        # if not overlap_found:
        #     doc.ents = ents
        #     db.add(doc)
        # else:
        #     print(f"Skipping document {i} due to overlapping entities.")

    db.to_disk("../data/train.spacy")

    return skipped


def train_model() -> Language:
    train_or_no: str = input(
        "Do you consent to the following command being run?:\npython -m spacy train config.cfg --output ../models --paths.train train.spacy --paths.dev train.spacy\n"
    )
    train_or_no = train_or_no.strip().lower()

    if train_or_no in ("y", "yes"):
        result: CompletedProcess[str] = subprocess.run(
            "python -m spacy train ../config/config.cfg --output ../../models --paths.train ../data/train.spacy --paths.dev ../data/train.spacy",
            shell=True,
            capture_output=True,
            check=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)

        if result.returncode == 0:
            return spacy.load("../../models/model-best")
        else:
            raise Exception("Training script failed.")
    else:
        raise Exception("Exiting, because user did not consent to training")


def test(nlp_ner: Language) -> None:
    # Example usage
    doc: Doc = nlp_ner("YBCO was synthesized using solid-state reaction method.")
    for ent in doc.ents:
        print(ent.text, ent.label_)


def main() -> None:
    nlp: Language = load_model()
    train_data: list[tuple] = load_train_data()
    dev_data: list[tuple] = load_dev_data()

    skipped_train: list[int] = data_to_binary(nlp, train_data)
    skipped_dev: list[int] = data_to_binary(nlp, dev_data)

    total_train: int = sum([len(tup[1]["entities"]) for tup in train_data])
    print(f"\n==========\nTrain\n\nSpan is None: {skipped_train[0]}")
    print(f"Overlap Found: {skipped_train[1]}")
    print(f"Total entities skipped: {sum(skipped_train)}")
    print(f"Total entities: {total_train}")
    print(
        f"Total entities in DocBin: {total_train - sum(skipped_train)}\n\n==========\n"
    )

    total_dev: int = sum([len(tup[1]["entities"]) for tup in dev_data])
    print(f"==========\nDev\n\nSpan is None: {skipped_dev[0]}")
    print(f"Overlap Found: {skipped_dev[1]}")
    print(f"Total entities skipped: {sum(skipped_dev)}")
    print(f"Total entities: {total_dev}")
    print(f"Total entities in DocBin: {total_dev - sum(skipped_dev)}\n\n==========\n")

    nlp_ner: Language = train_model()

    test(nlp_ner)


if __name__ == "__main__":
    main()
