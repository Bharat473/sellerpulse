"""One place for the embedding model and the Chroma store.

Ingestion (Task 8) and retrieval (Task 9) both import from here,
so they always use exactly the same model and settings.
"""
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
STORE_DIR = ".chroma"
COLLECTION = "sellerpulse"


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL,
                                 encode_kwargs={"normalize_embeddings": True})


def get_store():
    return Chroma(collection_name=COLLECTION, embedding_function=get_embeddings(),
                  persist_directory=STORE_DIR,
                  collection_metadata={"hnsw:space": "cosine"})
