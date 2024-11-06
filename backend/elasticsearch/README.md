# Setup of Elasticsearch

This guide provides steps for setting up Elasticsearch and Kibana using Docker Compose. The setup of elasticsearch is based on the Elastic blog article [Getting Started with the Elastic Stack and Docker Compose](https://www.elastic.co/blog/getting-started-with-the-elastic-stack-and-docker-compose).

## Table of Contents
- [Setup](#setup)
  - [Clone the Repository](#1-clone-the-repository)
  - [Set up .env File](#2-set-up-env-file)
  - [Install Docker](#3-install-docker)
  - [Run the Docker Container](#4-run-the-docker-container)
  - [Download ca_cert](#5-download-ca_cert)
  - [Access Kibana](#6-access-kibana-optional)
  - [Create API Key](#7-create-api-key)
- [Stopping the Docker Container](#stopping-the-docker-container)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Setup

### 1. Clone the Repository

Clone the repo and navigate to the elasticsearch directory

   ```bash
   git clone https://github.com/vikram087/icam-superconducticity-repository.git
   cd icam-superconducticity-repository/backend/elasticsearch
   ```

### 2. Set up `.env` File

Create a `.env` file to define environment variables required for the stack configuration.

   ```ini
   # Project namespace (defaults to the current folder name if not set)
   COMPOSE_PROJECT_NAME=myproject

   # Password for the 'elastic' user (at least 6 characters)
   ELASTIC_PASSWORD=changeme

   # Password for the 'kibana_system' user (at least 6 characters)
   KIBANA_PASSWORD=changeme

   # Version of Elastic products
   STACK_VERSION=8.15.0

   # Set the cluster name
   CLUSTER_NAME=docker-cluster

   # Set to 'basic' or 'trial' to automatically start the 30-day trial
   LICENSE=basic

   # Ports
   ES_PORT=9200
   KIBANA_PORT=5601

   # Memory limits
   ES_MEM_LIMIT=1073741824
   KB_MEM_LIMIT=1073741824

   # Encryption key (for POC environments only, if using, please change)
   ENCRYPTION_KEY=c34d38b3a14956121ff2170e5030b471551370178f43e5626eec58b04a30fae2
   ```

### 3. Install Docker

Install Docker Desktop for your operating system:

- **[Mac](https://docs.docker.com/desktop/install/mac-install/)**
- **[Windows](https://docs.docker.com/desktop/install/windows-install/)**
- **[Linux](https://docs.docker.com/desktop/install/linux/)**

### 4. Run the Docker Container

Start the Docker container.

   ```bash
   docker compose up -d
   ```

### 5. Download ca_cert

Dowload the certificate for a secure elasticsearch environment

   ```bash
   docker cp es01:/usr/share/elasticsearch/config/certs/ca/ca.crt ../server && cp ../server/ca.crt ../scripts/ca.crt
   ```

### 6. Access Kibana (optional)

After starting the Docker container, you can access Kibana at `http://localhost:5601`. Log in with:

   - **Username**: `elastic`
   - **Password**: the `ELASTIC_PASSWORD` from your `.env` file

### 7. Create API Key

This API key allows the server to securely communicate with Elasticsearch.

- **GUI (through Kibana)**

   1. Navigate to **Management > Stack Management > API Keys > Create API Key**.
   2. Create an API key with no restrictions, then copy it for the next step.
   3. Paste it into the .env file

- **Command Line**

Replace ${ELASTIC_PASSWORD} with your elasticsearch password, and "your-api-key" with your api key

   ```bash
   sudo curl --cacert ../server/ca.crt -X POST "https://localhost:9200/_security/api_key" \
   -H "Content-Type: application/json" \
   -u "elastic:${ELASTIC_PASSWORD}" \
   -d '{"name": "your-api-key"}' | jq -r .encoded >> ../.env
   ```

The command above automatically copies the api key to the file, if you wanna see the values after the command run the following (only copy the encoded value)

   ```bash
   sudo curl --cacert ../server/ca.crt -X POST "https://localhost:9200/_security/api_key" \
   -H "Content-Type: application/json" \
   -u "elastic:${ELASTIC_PASSWORD}" \
   -d '{"name": "your-api-key"}'
   ```

### Stopping the Docker Container

To stop the container, run:

   ```bash
   docker compose down
   ```

## Troubleshooting

- **Elasticsearch fails to start**: Ensure your machine has at least 4GB of free memory. You may need to adjust the memory limits in the `.env` file.
- **Kibana not accessible**: Verify the `KIBANA_PORT` (default is `5601`) is open on your system.

## Next Steps

- **Add Data to Elasticsearch**: You can ingest data via the Elasticsearch HTTP API.
- **Set Up Kibana Visualizations**: Use the Kibana dashboard to create visualizations and monitor your data.