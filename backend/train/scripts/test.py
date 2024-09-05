from spacy.language import Language
from spacy.tokens import Doc
import spacy


def load_model() -> Language:
    nlp: Language = spacy.load("../../models/model-best")

    return nlp


def test(nlp_ner: Language) -> None:
    # Example usage
    doc: Doc = nlp_ner("YBaCuO was synthesized using solid-state reaction method.")
    for ent in doc.ents:
        print(ent.text, ent.label_)


def main() -> None:
    nlp_ner: Language = load_model()

    test(nlp_ner)


if __name__ == "__main__":
    main()
