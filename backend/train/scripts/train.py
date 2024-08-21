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


def data_to_binary(nlp: Language, data: list[tuple]) -> None:
    db = DocBin()

    for text, annot in data:
        doc: Doc = nlp.make_doc(text)
        ents: list[Span] = []
        for start, end, label in annot["entities"]:
            span: Span | None = doc.char_span(
                start, end, label=label, alignment_mode="contract"
            )
            if span is None:
                print(f"Skipping entity {start, end, label}")
            else:
                ents.append(span)
        doc.ents = ents
        db.add(doc)

    db.to_disk("../data/train.spacy")


def train_model() -> Language:
    train_or_no: str = input(
        "Do you consent to the following command being run?:\npython -m spacy train config.cfg --output ../models --paths.train train.spacy --paths.dev train.spacy"
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

    data_to_binary(nlp, train_data)
    data_to_binary(nlp, dev_data)
    nlp_ner: Language = train_model()

    test(nlp_ner)


if __name__ == "__main__":
    main()
