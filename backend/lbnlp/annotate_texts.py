from lbnlp.models.load.matscholar_2020v1 import (
    load,
    NERClassifier,
)


def perform_analysis(ner_model: NERClassifier, abstract: dict):
    tags = ner_model.tag_doc(abstract)

    return tags


def main() -> None:
    abstract = "© 2016 WILEY-VCH Verlag GmbH & Co. KGaA, Weinheim. There is much current interest in combining superconductivity and spin-orbit coupling in order to induce the topological superconductor phase and associated Majorana-like quasiparticles which hold great promise towards fault-tolerant quantum computing. Experimentally these effects have been combined by the proximity-coupling of super-conducting leads and high spin-orbit materials such as InSb and InAs, or by controlled Cu-doping of topological insu-lators such as Bi2Se3. However, for practical purposes, a single-phase material which intrinsically displays both these effects is highly desirable. Here we demonstrate coexisting superconducting correlations and spin-orbit coupling in molecular-beam-epitaxy-grown thin films of GeTe. The former is evidenced by a precipitous low-temperature drop in the electrical resistivity which is quelled by a magnetic field, and the latter manifests as a weak antilocalisation (WAL) cusp in the magnetotransport. Our studies reveal several other intriguing features such as the presence of two-dimensional rather than bulk transport channels below 2 K, possible signatures of topological superconductivity, and unexpected hysteresis in the magnetotransport. Our work demonstrates GeTe to be a potential host of topological SC and Majorana-like excitations, and to be a versatile platform to develop quantum information device architectures."

    ner_model: NERClassifier = load("ner")
    tags = perform_analysis(ner_model, abstract)

    print(tags)


if __name__ == "__main__":
    main()

"""
The tokens in the doc are annotated as tuples according to the IOB (inside entity I, outside entity O, beginning of entity B) scheme to handle multi-token entities and the following entity tags

MAT: material
DSC: description of sample
SPL: symmetry or phase label
SMT: synthesis method
CMT: characterization method
PRO: property - may also include PVL (property value) or PUT (property unit)
APL: application
An example tag would be B-MAT meaning beginning of a material entity followed by I-MAT meaning a continuation of that material entity.V
"""
