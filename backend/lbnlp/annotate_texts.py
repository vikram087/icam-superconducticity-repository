#from lbnlp.models.load.matbert_ner_2021v1 import load
from lbnlp.models.load.matscholar_2020v1 import load

#bert_ner = load("solid_state")
ner_model = load("ner")

doc = "© 2016 WILEY-VCH Verlag GmbH & Co. KGaA, Weinheim. There is much current interest in combining superconductivity and spin-orbit coupling in order to induce the topological superconductor phase and associated Majorana-like quasiparticles which hold great promise towards fault-tolerant quantum computing. Experimentally these effects have been combined by the proximity-coupling of super-conducting leads and high spin-orbit materials such as InSb and InAs, or by controlled Cu-doping of topological insu-lators such as Bi2Se3. However, for practical purposes, a single-phase material which intrinsically displays both these effects is highly desirable. Here we demonstrate coexisting superconducting correlations and spin-orbit coupling in molecular-beam-epitaxy-grown thin films of GeTe. The former is evidenced by a precipitous low-temperature drop in the electrical resistivity which is quelled by a magnetic field, and the latter manifests as a weak antilocalisation (WAL) cusp in the magnetotransport. Our studies reveal several other intriguing features such as the presence of two-dimensional rather than bulk transport channels below 2 K, possible signatures of topological superconductivity, and unexpected hysteresis in the magnetotransport. Our work demonstrates GeTe to be a potential host of topological SC and Majorana-like excitations, and to be a versatile platform to develop quantum information device architectures."


# the MatBERT model is intended to be used with batches (multiple documents at once)
# so we just put the doc into a list before tagging

#tags = bert_ner.tag_docs([doc])
tags = ner_model.tag_doc(doc)

print(tags)
