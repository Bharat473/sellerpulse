"""Step B: compare two models on 4 eval questions, 5 runs each, with checks that verify facts.

Run from the repo root:
  uv run python simple/compare.py
"""
import os
import re
import time

from langchain_groq import ChatGroq

import sellerpulse as sp  # reuses the vector store, prompt and retrieval

MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
RUNS = 5
QUESTIONS = {  # one question per behaviour, with the check that decides PASS
    "diagnosis": ("Why is my Boho Wall Hanging listing underperforming?",
                  lambda a: bool(re.search(r"REV-\d+", a)) and not re.search(r"\b(sales|conversion|revenue)\b", a, re.I)),
    "policy": ("Can I offer buyers a free gift for leaving a 5-star review?",
               lambda a: "policy-2" in a and bool(re.search(r"\b(can't|cannot|not allowed|prohibited|not permitted)\b", a, re.I))),
    "no data": ("How did my sales perform last week?",
                lambda a: bool(re.search(r"(don't|do not) have|can't access|cannot access|not available|does not include|unable to", a, re.I))
                and not re.search(r"[€$]\s*\d|\d+\s*(%|units|orders|EUR|USD)", a)),
    "draft": ("Draft a reply to this 3-star review: 'Cute but smaller than expected for the price.'",
              lambda a: "DRAFT" in a and "Meera Iyer, Meera Home Studio" in a),
}
NUMBER_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
COUNT = re.compile(r"\b(two|three|four|five|six|\d+)\s+(?:\S+\s+){0,2}review(?:s|ers)?\b", re.I)
MEASURE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:cm|mm|inch|inches|in)\b|\b[XY]\s*(?:inches|cm)\b", re.I)


def wrong_count(answer, data):
    """A count is wrong if it differs from the review IDs cited in the same sentence,
    or (with no IDs in the sentence) is more than the reviews the model was given."""
    given = len(set(re.findall(r"REV-\d+", data)))
    for sentence in re.split(r"(?<=[.!?])\s+|\n", answer):
        for m in COUNT.finditer(sentence):
            n = NUMBER_WORDS.get(m.group(1).lower()) or int(m.group(1))
            ids = set(re.findall(r"REV-\d+", sentence))
            if (ids and n != len(ids)) or (not ids and n > given):
                return True
    return False


def invented_measure(answer, data):
    """A measurement (cm, inches) that does not appear in the Shop data was made up."""
    return any(m.group(1) is None or m.group(1) not in data for m in MEASURE.finditer(answer))


def ask(llm, messages):
    for _ in range(4):
        try:
            return llm.invoke(messages).content.replace("\u2011", "-").replace("\u2019", "'")
        except Exception as err:
            if "429" in str(err) or "rate" in str(err).lower():
                print("   (rate limit, waiting 30 s)")
                time.sleep(30)
            else:
                return f"ERROR: {err}"
    return "ERROR: rate limit"


rows = []
for model in MODELS:
    llm = ChatGroq(model=model, api_key=os.getenv("GROQ_API_KEY"), temperature=0, max_retries=0)
    for name, (question, check) in QUESTIONS.items():
        data = "\n\n".join(f"[{d.metadata['id']}] {d.page_content}" for d, _ in sp.retrieve(question))
        messages = [("system", sp.SYSTEM_PROMPT), ("human", f"Shop data:\n{data}\n\nQuestion: {question}")]
        answers = []
        for run in range(1, RUNS + 1):
            answers.append(ask(llm, messages))
            print(f"\n===== {model} | {name} | run {run}/{RUNS}\n{answers[-1]}")
            time.sleep(3)
        ok = [a for a in answers if not a.startswith("ERROR")]
        rows.append((model.split("/")[1], name, sum(check(a) for a in ok), sum(wrong_count(a, data) for a in ok),
                     sum(invented_measure(a, data) for a in ok), len(set(ok)), RUNS - len(ok)))

print(f"\n## Scorecard ({RUNS} runs per cell)\n")
print("| Model | Question | Behaviour PASS | Wrong counts | Invented measurements | Distinct answers | Errors |")
print("|---|---|---|---|---|---|---|")
for model, name, passed, wrong, invented, distinct, errors in rows:
    print(f"| {model} | {name} | {passed}/{RUNS} | {wrong} | {invented} | {distinct} | {errors} |")
