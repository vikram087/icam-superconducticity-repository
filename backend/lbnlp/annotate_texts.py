from lbnlp.models.load.matbert_ner_2021v1 import load

bert_ner = load("solid_state")

doc = (
    "Synthesis of carbon nanotubes by chemical vapor deposition over patterned "
    "catalyst arrays leads to nanotubes grown from specific sites on surfaces."
    "The growth directions of the nanotubes can be controlled by van der Waals "
    "self-assembly forces and applied electric fields. The patterned growth "
    "approach is feasible with discrete catalytic nanoparticles and scalable "
    "on large wafers for massive arrays of novel nanowires."
)

# the MatBERT model is intended to be used with batches (multiple documents at once)
# so we just put the doc into a list before tagging
tags = bert_ner.tag_docs([doc])


print(tags)
