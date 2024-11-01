# Setup of Backend (Elasticsearch, Server, Scripts, and Models)

Important: If you choose to use Docker for your configuration, you just need to configure .env files and go through the docker setup for the whole project, if you 
want to build from source, you still have to use docker (sorry 😢), but just for Elasticsearch and Kibana, and you can setup the Server, Scripts, and Models as described
in the READMEs. Good luck, this backend was not easy to setup from scratch 🫡

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