# Superconductivity Paper Search Engine - Backend

## Overview

This is the backend component of the Superconductivity Paper Search Engine. It handles data processing, search operations, and serves as an API for the frontend.

## Features

- **Vector Search**: Implements HNSW algorithm for efficient similarity searches
- **Natural Language Processing**: Uses sentence transformers for query embedding
- **Caching**: Utilizes Redis for optimized performance
- **Fuzzy Search**: Implements fuzzy search for authors and categories
- **LLaMA-3 Integration**: Generates answers to specific questions based on paper abstracts

## Technologies Used

- **Python**: Core scripting language
- **Flask**: Web framework for the API
- **Elasticsearch**: Database for storing and searching paper metadata and embeddings
- **ArXiv API**: For compiling paper metadata
- **Sentence Transformer**: For embedding queries
- **Redis**: For caching and performance optimization
- **LLaMA-3**: Large language model for generating answers to questions
- **Docker**: For containerization and local hosting of Elasticsearch

## Performance

- Achieves 91% faster fetching for cached results using Redis

## Contact

- **Lead Developer**: Vikram Penumarti (vpenumarti@ucdavis.edu)