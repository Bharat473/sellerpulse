"""Retrieval: work out which listing a question is about, then fetch the closest chunks.

Every search is filtered by seller_id, so a seller only ever sees their own data.
"""
import pandas as pd

from src.vectorstore import get_store

LISTINGS = pd.read_csv("data/synthetic/listings.csv")
K = 3


def find_sku(question, seller_id):
    """Return the SKU of the one listing named in the question; None if none or several match."""
    q = question.lower()
    mine = LISTINGS[LISTINGS.seller_id == seller_id]
    matches = [r.sku for r in mine.itertuples() if r.title.split(" - ")[0].lower() in q]
    return matches[0] if len(matches) == 1 else None


def retrieve(question, seller_id, k=K):
    """Return (sku, [(document, distance), ...]) for this seller's closest chunks."""
    sku = find_sku(question, seller_id)
    if sku:
        where = {"$and": [{"seller_id": seller_id}, {"sku": sku}]}
    else:
        where = {"seller_id": {"$in": [seller_id, "all"]}}
    return sku, get_store().similarity_search_with_score(question, k=k, filter=where)
