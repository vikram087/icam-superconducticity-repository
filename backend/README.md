# Setup of Backend (Elasticsearch, Server, Scripts, and Models)

Important: 

If you want to use the full Docker setup, run the v1 Docker Compose file first, setup your API Key, add it to the .env file, destroy the config,
then run the latest Docker Compose file. It is designed like this because elasticsearch must be fully setup including api key (must be done manually) to successfully run the 
backend server and scripts. 

You could theoretically run the latest Docker Compose, setup your API Key in elasticsearch, add it to the .env file, destroy the config, then run the same Docker Compose 
setup, but this would take a little longer.

The v1 Docker Compose is the same as latest, except without frontend and backend setup, just elasticsearch.

## Table of Contents

- [Create API Key](#1-create-api-key)
- [Set up .env File](#2-set-up-env-file)
- [Elasticsearch/Docker](./config/README.md)
- [Server](./server/README.md)
- [Scripts](./scripts/README.md)
- [Models](./lbnlp/README.md)

### 1. Create API Key

Reference steps from step 7. [Create API Key](../config/README.md)

### 2. Set up `.env` File

Create a `.env` file for the Python Elasticsearch API. Replace `YOUR_API_KEY_HERE` with the API key you obtained.

   ```ini
    # API key for Elasticsearch
    API_KEY=YOUR_API_KEY_HERE

    # url for elasticsearch, defaults to https://localhost:9200
    ES_URL=https://localhost:9200

    # hard-coded value
    DOCKER=false
   ```