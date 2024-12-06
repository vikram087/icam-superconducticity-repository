# Kubernetes Setup Guide

This guide provides steps for setting up the ICAM Materials Database project using Kubernetes.

> Note: This setup is currently in progress, so it is not complete

## Table of Contents
- [Setup](#setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Configure Environment Files](#2-configure-environment-files)
  - [3. Install Docker](#3-install-docker)
  - [4. Deploy to Kubernetes](#4-deploy-to-kubernetes)
  - [5. Access Kibana (Optional)](#5-access-kibana-optional)
- [Stopping the Kubernetes Pods](#stopping-the-kubernetes-pods)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Setup

### 1. Clone the Repository

Clone the repository and navigate to the `kubernetes` configuration directory.

```bash
git clone https://github.com/vikram087/icam-materials-database.git
cd icam-materials-database/kubernetes
```

### 2. Configure Environment Files

#### Create a `.env.config` file

Define non-sensitive environment variables in `.env.config`:

```ini
# Project namespace (defaults to the current folder name if not set)
COMPOSE_PROJECT_NAME=icam

# Version of Elastic products
STACK_VERSION=8.15.0

# Set the cluster name
CLUSTER_NAME=icam-cluster

# License type for Elastic products ('basic' or 'trial' for 30-day trial)
LICENSE=basic

# Ports
ES_PORT=9200
KIBANA_PORT=5601

# Memory limits in bytes
ES_MEM_LIMIT=1073741824
KB_MEM_LIMIT=1073741824

# Backend URL (use public DNS/IP if on cloud instance)
VITE_BACKEND_URL=http://localhost:8080

# Kibana URL (default: http://localhost:5601)
KIBANA_URL=http://localhost:5601

# Name of the Elasticsearch index
INDEX=icam-index
```

#### Create a `.env.secret` file

Define sensitive environment variables in `.env.secret`:

```ini
# Password for the 'elastic' user (minimum 6 characters)
ELASTIC_PASSWORD=changeme

# Password for the 'kibana_system' user (minimum 6 characters)
KIBANA_PASSWORD=changeme

# Encryption key for security (change this for production environments)
ENCRYPTION_KEY=c34d38b3a14956121ff2170e5030b471551370178f43e5626eec58b04a30fae2

# Your API key
API_KEY=your-api-key
```

### 3. Set up ConfigMap and Secret in Kubernetes

#### Create the Secret

To store sensitive information in Kubernetes as a secret, use the `.env.secret` file:

```bash
kubectl create secret generic icam-secret --from-env-file=.env.secret
```

#### Create the ConfigMap

To store configuration data, create a ConfigMap from `.env.config`:

```bash
kubectl create configmap icam-config --from-env-file=.env.config
```

### 4. Deploy to Kubernetes

Ensure Docker is installed and then run:

```bash
# Verify Docker is running
docker --version

# Deploy to Kubernetes
kubectl apply -f .
```

### 5. Access Kibana (Optional)

To access Kibana, retrieve the external IP (if available) or use port forwarding:

```bash
kubectl port-forward svc/kibana-service 5601:5601
```

Then, visit [http://localhost:5601](http://localhost:5601) in your browser.

## Stopping the Kubernetes Pods

To stop the Kubernetes deployment and delete resources:

```bash
kubectl delete -f .
```

## Troubleshooting

- **Check Pod Logs**: For troubleshooting errors, check logs for individual pods:
  ```bash
  kubectl logs <pod-name>
  ```
- **Describe Pod**: For detailed information about why a pod might not be running:
  ```bash
  kubectl describe pod <pod-name>
  ```

## Next Steps

After verifying the deployment, consider securing your environment further, configuring autoscaling, and setting up monitoring tools like Prometheus and Grafana.