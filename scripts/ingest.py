"""Ingest the RAG corpus into Chroma (Task 8).

Reads corpus/*.jsonl, splits, embeds with bge-small and stores in .chroma/.
Rebuilds from scratch on every run. Run from the repo root:
    uv run python -m scripts.ingest
"""
import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.vectorstore import get_store

CORPUS = Path("corpus")
FILES = ["listings", "reviews", "policy"]


def load_docs():
    docs = []
    for name in FILES:
        rows = [json.loads(line) for line in (CORPUS / f"{name}.jsonl").read_text().splitlines()]
        docs += [Document(page_content=r["text"], metadata=r["metadata"] | {"id": r["id"]})
                 for r in rows]
        print(f"  {name:9} {len(rows):4} documents")
    return docs


def main():
    docs = load_docs()
    print(f"Loaded {len(docs)} documents")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    store = get_store()
    store.reset_collection()   # empty it first: re-runs rebuild instead of duplicating
    print(f"Embedding size: {len(store.embeddings.embed_query('test'))}")
    store.add_documents(chunks)
    print(f"Chroma collection now holds {len(store.get()['ids'])} chunks")

    hit = store.similarity_search("Boho wall hanging smaller than expected", k=1)[0]  # smoke test
    print(f"Smoke test top hit: {hit.page_content.splitlines()[0]}")


if __name__ == "__main__":
    main()
