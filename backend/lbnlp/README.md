## LBNLP
##### Lawrence Berkeley National Lab Natural Language Processing
###### Common text mining tools for materials science and chemistry, for groups at Lawrence Berkeley National Lab (LBNL) and beyond.

<img src="./docs_src/static/lbnlp_logo.png" alt="logo" width="300"/>

#### Warning: This package is being migrated/condensed from several source repos. It is non-working at the moment. This warning will be removed when it is ready for public usage.

- [Documentation](https://lbnlp.github.io/lbnlp)

MODEL NOTES:

- downgraded from pymatgen from 2019.9.8 -> 2018.11.30
- python version 3.7.17
- ubuntu 22.04 amd64, t2.xlarge (4vcpu, 16GiB mem)
- had to edit site package for pdfminer 
before:

#from importlib.metadata import version, PackageNotFoundError

after:

from importlib_metadata import version, PackageNotFoundError

- had to run cde data download to download chemdataextractor model
- installed requirements.txt, requirements-matscholar_2020v1.txt
- ran setup.py install and setup.py build after deps installed
- had to move annotate_texts into lbnlp dir for imports

git clone https://github.com/vikram087/icam-superconducticity-repository.git
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.7
sudo apt install python3.7-venv
python3.7 -m venv venv3.7.17
source venv3.7.17/bin/activate
sudo apt install build-essential
sudo apt install python3.7-dev
pip install -r requirements.txt
pip install -r requirements-matscholar_2020v1.txt
python setup.py install
python setup.py build
maybe: pip install urllib3==1.26.20
maybe: pip install protobuf==3.20.3
edit site package
cde data download
python annotate_texts.py