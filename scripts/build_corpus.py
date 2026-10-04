"""Build the RAG corpus (Task 7): one document per listing, per review and per policy section.

Text only. Prices, stock and sales stay out: figures come from tools in Week 2.
Run from the repo root: uv run python scripts/build_corpus.py
"""
import json
from pathlib import Path

import pandas as pd

DATA = Path("data/synthetic")
OUT = Path("corpus")
POLICY = OUT / "source" / "seller_policy.md"


def write(name, docs):
    with open(OUT / f"{name}.jsonl", "w") as f:
        for doc in docs:
            f.write(json.dumps(doc) + "\n")
    print(f"  {name:9} {len(docs):4} documents")


def listing_docs(listings):
    return [{"id": f"listing-{r.sku}",
             "text": f'Listing "{r.title}" ({r.sku}), category {r.category}:\n{r.description}',
             "metadata": {"type": "listing", "seller_id": r.seller_id, "sku": r.sku, "title": r.title}}
            for r in listings.itertuples()]


def review_docs(reviews, titles):
    docs = []
    for r in reviews.itertuples():
        day = pd.Timestamp(r.review_date).strftime("%-d %b %Y")
        docs.append({"id": f"review-{r.review_id}",
                     "text": f'Review {r.review_id} of "{titles[r.sku]}" ({r.sku}), {r.rating} stars, {day}:\n{r.comment}',
                     "metadata": {"type": "review", "seller_id": r.seller_id, "sku": r.sku,
                                  "title": titles[r.sku], "review_id": r.review_id,
                                  "rating": int(r.rating), "date": r.review_date}})
    return docs


def policy_docs():
    sections = POLICY.read_text().split("\n## ")[1:]   # everything after each "## " heading
    docs = []
    for s in sections:
        heading, body = s.split("\n", 1)
        docs.append({"id": f"policy-{heading.split('.')[0]}",
                     "text": f"Setukart seller policy, section {heading}:\n{body.strip()}",
                     "metadata": {"type": "policy", "seller_id": "all", "section": heading}})
    return docs


def main():
    listings = pd.read_csv(DATA / "listings.csv")
    reviews = pd.read_csv(DATA / "reviews.csv")
    titles = dict(zip(listings.sku, listings.title))
    print("Corpus written to corpus/:")
    write("listings", listing_docs(listings))
    write("reviews", review_docs(reviews, titles))
    write("policy", policy_docs())


if __name__ == "__main__":
    main()
