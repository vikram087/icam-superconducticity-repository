import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy.training import Example

# Load pre-trained spaCy transformer model
nlp = spacy.load("en_core_web_trf")

# Define custom entity labels
custom_labels = [
    "THEORY", "EXPERIMENT", "COMPUTATION",
    "PHENOMENA", "PHASE", "PROPERTY",
    "CHEMICAL_FORMULA", "LATTICE", "CRYSTAL_STRUCTURE",
    "SPECIFIC_PROPERTY", "THEORETICAL_TECHNIQUE",
    "EXPERIMENTAL_TECHNIQUE_CHARACTERIZATION", "EXPERIMENTAL_TECHNIQUE_GROWTH"
]

# Example training function
def train_custom_ner(nlp, train_data, labels):
    # Get the named entity recognizer from the pipeline
    ner = nlp.get_pipe("ner")

    # Add new entity labels to the recognizer
    for label in labels:
        ner.add_label(label)

    # Create an optimizer
    optimizer = nlp.resume_training()

    # Training loop
    for itn in range(10):
        losses = {}
        for text, annotations in train_data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], sgd=optimizer, losses=losses)
        print(f"Iteration {itn}, Losses: {losses}")
    
    return nlp

# Placeholder for training data and training the NER model
train_data = [
    ("This study uses Density Functional Theory (DFT) to investigate the properties of H2O.", {"entities": [(16, 42, "THEORETICAL_TECHNIQUE"), (68, 71, "CHEMICAL_FORMULA")]}),
    # Add more annotated examples
]

nlp = train_custom_ner(nlp, train_data, custom_labels)

# Define rule-based patterns for matching
matcher = Matcher(nlp.vocab)

# Example pattern definitions (expand these with actual patterns)
patterns = {
    "PHENOMENA": [{"LOWER": {"IN": ["metal", "insulator", "superconductor", "ferromagnet", "antiferromagnet", "spin-glass"]}}],
    "THEORETICAL_TECHNIQUE": [{"LOWER": "density"}, {"LOWER": "functional"}, {"LOWER": "theory"}],
    "EXPERIMENTAL_TECHNIQUE_CHARACTERIZATION": [{"LOWER": {"IN": ["x-ray", "neutron", "raman", "infrared", "stm", "afm", "magnetometer", "squid"]}}],
    "EXPERIMENTAL_TECHNIQUE_GROWTH": [{"LOWER": "crystal"}, {"LOWER": "growth"}],
    # Add more patterns for other categories
}

# Add patterns to matcher
for label, pattern in patterns.items():
    matcher.add(label, [pattern])

# Custom pipeline component to apply matcher
def custom_component(doc):
    matches = matcher(doc)
    spans = [Span(doc, start, end, label=nlp.vocab.strings[match_id]) for match_id, start, end in matches]
    doc.ents = list(doc.ents) + spans
    return doc

# Add custom component to pipeline
nlp.add_pipe(custom_component, after="ner")

# Process a batch of abstracts
abstracts = [
    "This study uses Density Functional Theory (DFT) to investigate the properties of H2O.",
    "The material exhibits superconducting properties with a transition temperature of 5K."
]

for abstract in abstracts:
    doc = nlp(abstract)
    for ent in doc.ents:
        print(ent.text, ent.label_)

# Expected Output:
# Density Functional Theory THEORETICAL_TECHNIQUE
# H2O CHEMICAL_FORMULA
# superconducting PHENOMENA
# transition temperature SPECIFIC_PROPERTY
