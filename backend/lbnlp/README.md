# Setup of Lbnlp Models (Matbert, Matscholar, Relevance)

This guide provides steps for setting up Lbnlp models, useful for NER tasks on materials science texts. Original repositories:

- [Lbnlp main repo (Matbert, Matscholar, Relevance implementation)](https://github.com/lbnlp/lbnlp)
- [Lbnlp Matbert Repo (model download)](https://github.com/lbnlp/MatBERT)
- [CederGroupHub Matbert Repo (model testing/training)](https://github.com/CederGroupHub/MatBERT_NER)

## Table of Contents

- [Prereqs](#prereqs)
- [Common Setup (Required for all 3 models)](#common-setup-required-for-all-3-models)
- [Matbert](#matbert)
- [Matscholar/Relevance](#matscholarrelevance)

## Prereqs
- **Architecture**: Machine running `amd64` (tested on Ubuntu 22.04 amd64, t2.medium (2vcpu, 8GiB mem))

## Common Setup (Required for all 3 models)

1. **Clone the repository**

   Clone the repo and navigate to the lbnlp directory.

   ```bash
   git clone https://github.com/vikram087/icam-superconducticity-repository.git
   cd icam-superconducticity-repository/backend/lbnlp
   ```

2. **Install system dependencies**

   Install necessary dependencies for Python 3.7 and building packages.

   ```bash
   sudo apt update 
   sudo add-apt-repository ppa:deadsnakes/ppa 
   sudo apt install python3.7 python3.7-venv python3.7-dev build-essential
   ```

3. **Install Python dependencies for the chosen model**

   Choose the model-specific dependencies: [Matbert](#matbert) or [Matscholar/Relevance](#matscholarrelevance).

---

4. **Edit pdfminer library** 

   > **Note**: If you encounter import errors with `pdfminer`, edit the `__init__.py` file as follows:

   ```bash
   vim <environment path>/lib/python3.7/site-packages/pdfminer/__init__.py
   ```

   Replace:
   ```python
   from importlib.metadata import version, PackageNotFoundError
   ```
   With:
   ```python
   from importlib_metadata import version, PackageNotFoundError
   ```

5. **Download chemdataextractor models**  

   Download the required data for `chemdataextractor`.

   ```bash
   cde data download
   ```

6. **Test the setup**

   Run a test to verify that everything is set up correctly:

   ```bash
   python annotate_texts.py --model-type <model type>
   ```
   Replace `<model type>` with the model you want to test (`matbert`, `matscholar`, or `relevance`).

## Matbert

**Set up Python environment and install dependencies:**

```bash
python3.7 -m venv <environment path>
source <environment path>/bin/activate
pip install -r requirements.txt
pip install -r requirements-matbert_ner_2021v1.txt
```

## Matscholar/Relevance

**Set up Python environment and install dependencies:**

```bash
python3.7 -m venv <environment path>
source <environment path>/bin/activate
pip install -r requirements.txt
pip install -r requirements-matscholar_2020v1.txt
```
