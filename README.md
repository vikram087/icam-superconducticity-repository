# Superconductivity Paper Search Engine

## Overview

This project is a comprehensive search engine for superconductivity papers. It combines advanced search capabilities with natural language processing to provide an efficient and user-friendly way to explore scientific literature in the field of superconductivity.

## Features

- **Vector Search**: Utilizes HNSW (Hierarchical Navigable Small World) algorithm for efficient similarity searches.
- **Sorting and Filtering**: Allows users to sort results by relevance or date, and filter based on various criteria including date range.
- **Pagination**: Implements paginated results with customizable results per page.
- **Natural Language Processing**: Employs a sentence transformer for query embedding and LLaMA-3 model for generating answers to specific questions based on paper abstracts.
- **Caching**: Uses Redis for optimized performance, achieving 91% faster fetching for cached results.
- **Fuzzy Search**: Implements fuzzy search for authors and categories to improve search flexibility.

## Quick Start
...

## Architecture

### Backend
- **Python**: Core scripting language
- **Flask**: Web framework for the backend API
- **Elasticsearch**: Database for storing and searching paper metadata and embeddings
- **ArXiv API**: Used for compiling paper metadata
- **Sentence Transformer**: For embedding queries
- **Redis**: For caching and performance optimization
- **LLaMA-3**: Large language model for generating answers to questions

### Frontend
- **React.js**: JavaScript library for building the user interface

### Deployment
- **Docker**: Used for containerization and local hosting of Elasticsearch

## Usage

### Searching
- For titles and abstracts: Use context-based queries rather than keywords for better results.
- For authors and categories: Use keyword-based searches.

### Filtering
- Date Range: Use the date picker to filter papers within a specific time frame.

### Sorting
- Sort results by relevance or publication date using the dropdown menu.

### Pagination
- Customize results per page using the dropdown.
- Navigate through pages using the pagination controls.

### Performance Tips
- The search time increases with higher page numbers. For optimal performance, refine your search queries to find relevant results on earlier pages.
- Cached results are fetched 91% faster, so frequently accessed papers will load more quickly.

## Performance

- 91% faster fetching for cached results using Redis

## License
...

## Contact

- **Lead Developer**: Vikram Penumarti (vpenumarti@ucdavis.edu)