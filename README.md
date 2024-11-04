### Superconductivity Paper Search Engine

*This project currently has a single maintainer, so please anticipate some wait time for bug fixes and updates.*

---

## Overview

This project is a **comprehensive search engine for superconductivity papers**. It combines **advanced search capabilities** with **natural language processing (NLP)** for an efficient, user-friendly way to explore scientific literature in the superconductivity field.

## Key Features

- **Vector Search**: Uses the **HNSW (Hierarchical Navigable Small World)** algorithm for efficient similarity-based searches.
- **Advanced Sorting & Filtering**: Sort results by relevance or date and filter by criteria like date range.
- **Flexible Pagination**: Customizable results per page for a smooth browsing experience.
- **Natural Language Processing**: **Sentence Transformer** for embedding queries and **MatBERT** for extracting key properties from abstracts.
- **Caching for Speed**: **Redis** caching optimizes performance, achieving a **91% improvement in fetching speed** for cached results.
- **Fuzzy Search Capabilities**: Enhances author and category searches, increasing search flexibility.
- **Custom Search Syntax**: Allows for more refined and targeted searches.

## Architecture

### Backend Stack
- **Python**: Core scripting language.
- **Flask**: Backend API framework.
- **Elasticsearch**: Database for paper metadata and embeddings.
- **ArXiv API**: Data source for paper metadata.
- **Sentence Transformer**: Embeds query for similarity search.
- **Redis**: Caching for high performance.
- **MatBERT**: NER model for property extraction.

### Frontend Stack
- **React.js**: Library for a responsive and intuitive user interface.

### Deployment
- **Docker**: Containerization and local hosting of **Elasticsearch**.

## Setup

> ⚡ **Getting Started**  
> Follow the README files below for manual setup instructions:

- [Frontend Setup](./frontend/README.md)
- [Backend Setup](./backend/README.md)

> 🐳 **Docker Supported!**  
- [Docker Setup](./docker/README.md)

## Contact Information

For questions or bug reports, please contact the lead developer:

- **Lead Developer**: **Vikram Penumarti**  
- **Email**: [vpenumarti@ucdavis.edu](mailto:vpenumarti@ucdavis.edu)

## Contribution

This project is currently maintained by a single developer. If there is enough community interest, contributions may be opened to outside collaborators. For inquiries or to express interest in contributing, please reach out to **vpenumarti@ucdavis.edu**.