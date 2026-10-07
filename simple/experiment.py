"""Non-determinism experiments: ask the same question N times per variant and score the answers.

Run from the repo root:
  uv run python simple/experiment.py            # all variants
  uv run python simple/experiment.py V2 V3      # only some variants
"""
import os
import re
import sys
import time

from langchain_groq import ChatGroq

import sellerpulse as sp  # builds the vector store once, reuses its prompt and retrieval

QUESTION = "Why is my Boho Wall Hanging listing underperforming?"
RUNS = 5
VARIANTS = {  # each variant changes ONE thing compared with V0
    "V0": {"desc": "baseline (current file)"},
    "V1": {"desc": "remove duplicate reviews", "dedupe": True},
    "V2": {"desc": "fixed seed 42", "seed": 42},
    "V3": {"desc": "smaller model gpt-oss-20b", "model": "openai/gpt-oss-20b"},
    "V4": {"desc": "reasoning effort low", "effort": "low"},
}

# Simple checks a human would otherwise do by reading every answer
COUNT = re.compile(r"\b(two|three|four|five|several|multiple|\d+)\s+(?:\S+\s+){0,2}review(?:s|ers)?\b", re.I)
SALES = re.compile(r"\b(sales|conversion|revenue|visibility|traffic)\b", re.I)
IDS = re.compile(r"REV-\d+")


def shop_data(dedupe):
    """The same Shop data block answer() builds; optionally drop reviews whose text repeats."""
    seen, parts = set(), []
    for doc, _ in sp.retrieve(QUESTION):
        comment = doc.page_content.split("\n", 1)[1]
        if dedupe and comment in seen:
            continue
        seen.add(comment)
        parts.append(f"[{doc.metadata['id']}] {doc.page_content}")
    return "\n\n".join(parts)


def ask(llm, messages):
    """Call Groq; wait and retry if the free-tier rate limit is hit."""
    for _ in range(4):
        try:
            return llm.invoke(messages).content
        except Exception as err:
            if "429" in str(err) or "rate" in str(err).lower():
                print("   (rate limit, waiting 30 s)")
                time.sleep(30)
            else:
                return f"ERROR: {err}"
    return "ERROR: rate limit"


def run_variant(name, v):
    llm = ChatGroq(model=v.get("model", sp.MODEL), api_key=os.getenv("GROQ_API_KEY"), temperature=0,
                   max_retries=0, reasoning_effort=v.get("effort"),
                   model_kwargs={"seed": v["seed"]} if "seed" in v else {})
    data = shop_data(v.get("dedupe", False))
    allowed = set(IDS.findall(data))
    messages = [("system", sp.SYSTEM_PROMPT), ("human", f"Shop data:\n{data}\n\nQuestion: {QUESTION}")]
    answers = []
    for run in range(1, RUNS + 1):
        text = ask(llm, messages)
        answers.append(text)
        print(f"\n===== {name} ({v['desc']}) run {run}/{RUNS}\n{text}")
        time.sleep(3)
    ok = [a for a in answers if not a.startswith("ERROR")]
    return {"count": sum(bool(COUNT.search(a)) for a in ok),
            "sales": sum(bool(SALES.search(a)) for a in ok),
            "unknown_ids": sum(bool(set(IDS.findall(a)) - allowed) for a in ok),
            "distinct": len(set(ok)), "errors": RUNS - len(ok)}


if __name__ == "__main__":
    chosen = sys.argv[1:] or list(VARIANTS)
    results = {name: run_variant(name, VARIANTS[name]) for name in chosen}
    print(f"\n## Scorecard ({RUNS} runs each, lower is better except where noted)\n")
    print("| Variant | Change | Count claims | Sales/conversion claims | Unknown IDs | Distinct answers | Errors |")
    print("|---|---|---|---|---|---|---|")
    for name, r in results.items():
        print(f"| {name} | {VARIANTS[name]['desc']} | {r['count']}/{RUNS} | {r['sales']}/{RUNS} | "
              f"{r['unknown_ids']}/{RUNS} | {r['distinct']} | {r['errors']} |")
