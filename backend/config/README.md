# Setup of Elasticsearch and Kibana

This guide provides steps for setting up an Elasticsearch and Kibana stack using Docker Compose, useful for centralized logging, monitoring, and search capabilities. The setup is based on the Elastic blog article [Getting Started with the Elastic Stack and Docker Compose](https://www.elastic.co/blog/getting-started-with-the-elastic-stack-and-docker-compose).

## Table of Contents
- [Setup](#setup)
  - [Clone the Repository](#clone-the-repository)
  - [Set up .env File](#set-up-env-file)
  - [Install Docker](#install-docker)
  - [Run the Docker Container](#run-the-docker-container)
  - [Access Kibana](#access-kibana)
  - [Stop the Docker Container](#stop-the-docker-container)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Setup

### 1. Clone the Repository

Clone the repo and navigate to the config directory

   ```bash
   git clone https://github.com/vikram087/icam-superconducticity-repository.git
   cd icam-superconducticity-repository/backend/config
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

   # Encryption key (for POC environments only)
   ENCRYPTION_KEY=c34d38b3a14956121ff2170e5030b471551370178f43e5626eec58b04a30fae2
   ```

### 3. Install Docker

Install Docker Desktop for your operating system:

- **[Mac](https://docs.docker.com/desktop/install/mac-install/)**
- **[Windows](https://docs.docker.com/desktop/install/windows-install/)**
- **[Linux](https://docs.docker.com/desktop/install/linux/)**

### 4. Run the Docker Container

Start the Docker container for Elasticsearch and Kibana.

   ```bash
   docker compose up -d
   ```

### 5. Download ca_cert

   ```bash
   docker cp config-es01-1:/usr/share/elasticsearch/config/certs/ca/ca.crt ./.
   ```

### 6. Access Kibana

After starting the Docker container, you can access Kibana at `http://localhost:5601`. Log in with:

   - **Username**: `elastic`
   - **Password**: the `ELASTIC_PASSWORD` from your `.env` file

### 6. Stop the Docker Container

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