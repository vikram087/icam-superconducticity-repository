# Use Ubuntu with specific platform
# FROM --platform=linux/amd64 ubuntu:22.04
FROM ubuntu:22.04

# Install Python 3.7 and dependencies in a single RUN statement
RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt install -y python3.7 python3.7-venv python3.7-dev build-essential git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt requirements-matbert_ner_2021v1.txt /app/

# Create virtual environment and install dependencies
RUN python3.7 -m venv /app/venv-matbert && \
    /app/venv-matbert/bin/pip install -r /app/requirements.txt -r /app/requirements-matbert_ner_2021v1.txt

# Copy the rest of the application files
COPY . /app/

# Set entrypoint to use virtualenv and run the script
# CMD ["/app/venv-matbert/bin/python", "annotate_texts.py", "--model-type", "matbert"]
