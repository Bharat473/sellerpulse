"""Task 9: retrieval test on the Boho question, unfiltered vs filtered.

Run from the repo root and save the log as evidence:
    uv run python -m scripts.test_retrieval | tee docs/task9-retrieval-test.md
"""
from src.retrieval import K, find_sku, retrieve
from src.vectorstore import get_store

QUESTION = "Why is my Boho Wall Hanging listing underperforming?"
SELLER = "S001"


def show(title, hits):
    print(f"\n## {title}\n")
    for rank, (doc, distance) in enumerate(hits, 1):
        m = doc.metadata
        text = doc.page_content.replace("\n", " ")
        print(f"{rank}. `{m['id']}` seller {m['seller_id']}, distance {distance:.3f}")
        print(f"   {text}")


def main():
    print("# Task 9: retrieval test\n")
    print(f"- Question: {QUESTION}")
    print(f"- Seller: {SELLER}, k = {K}")
    print(f"- Name lookup found: {find_sku(QUESTION, SELLER)}")

    show("A. Unfiltered (no seller or SKU filter)",
         get_store().similarity_search_with_score(QUESTION, k=K))
    sku, hits = retrieve(QUESTION, SELLER)
    show(f"B. Filtered (seller_id = {SELLER}, sku = {sku})", hits)

    print("\n## Judgment\n")
    print("- A: (fill in: correct/incorrect and why)")
    print("- B: (fill in: correct/incorrect and why)")


if __name__ == "__main__":
    main()
