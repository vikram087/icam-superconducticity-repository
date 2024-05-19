from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load environment variables
load_dotenv()
API_KEY = os.getenv('API_KEY')

# Initialize Elasticsearch client
client = Elasticsearch(
    "https://localhost:9200",
    api_key=API_KEY,
    ca_certs="./ca.crt"
)

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def faissImplementation(queryEmbedding, documentEmbeddings, k):
    # Ensure embeddings are numpy arrays and correct dimensions
    documentEmbeddings = np.array(documentEmbeddings).astype('float32')
    queryEmbedding = np.array([queryEmbedding]).astype('float32')

    d = documentEmbeddings.shape[1]  # Dimensionality of the vectors
    nb = documentEmbeddings.shape[0]  # Number of database vectors

    # Number of centroids
    nlist = 100

    # Build the index
    quantizer = faiss.IndexFlatL2(d)  # the other index
    index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)

    # Train the index
    index.train(documentEmbeddings)

    # Add vectors to the index
    index.add(documentEmbeddings)

    # Ensure the index is trained and has vectors
    assert index.is_trained
    assert index.ntotal == nb

    # Perform the search
    D, I = index.search(queryEmbedding, k)  # queryEmbedding is the query vector, k is the number of nearest neighbors

    # Sort the results by distance (similarity score)
    sorted_indices = np.argsort(D[0])  # Sort distances
    sorted_distances = D[0][sorted_indices]
    sorted_indices = I[0][sorted_indices]

    return sorted_distances, sorted_indices

def getAllEmbeddings():
    # Retrieve all embeddings from Elasticsearch
    response = client.search(query={"match_all": {}}, index="search-papers-meta", size=1000)  # Adjust the size as needed
    docs = response['hits']['hits']
    embeddings = [doc['_source']['embedding'] for doc in docs]
    abstracts = [doc['_source']['summary'] for doc in docs]
    return embeddings, abstracts

# Encode the query
queryEmbedding = model.encode("superconductivity")

# Retrieve document embeddings and abstracts
documentEmbeddings, abstracts = getAllEmbeddings()
documentEmbeddings = documentEmbeddings[0:100]  # Limiting the embeddings to the first 100 for this example

# Perform the FAISS search
distances, indices = faissImplementation(queryEmbedding, documentEmbeddings, 20)

# Print abstracts and their similarity scores
print("Top 20 results:")
for dist, idx in zip(distances, indices):
    print(f"Abstract: {abstracts[idx]}")
    print(f"Similarity Score: {dist}")
    print("\n")