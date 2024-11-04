# Setup of Backend (Elasticsearch, Server, Scripts, and Models)

## Table of Contents

- [Create API Key](#1-create-api-key)
- [Set up .env File](#2-set-up-env-file)
- [Elasticsearch](./elasticsearch/README.md)
- [Server](./server/README.md)
- [Scripts](./scripts/README.md)
- [Models](./models/README.md)

### 1. Create API Key

Reference steps from step 7. [Create API Key](./elasticsearch/README.md)

### 2. Set up `.env` File

Create a `.env` file for the Python Elasticsearch API. Replace `YOUR_API_KEY_HERE` with the API key you obtained.

   ```ini
    # API key for Elasticsearch
    API_KEY=YOUR_API_KEY_HERE

    # url for elasticsearch, defaults to https://localhost:9200
    ES_URL=https://localhost:9200

    # hard-coded value
    DOCKER=false

    # location of the NLP server to annotate texts
    LBNLP_URL=http://localhost:8000
   ```