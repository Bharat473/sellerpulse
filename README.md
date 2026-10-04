# SellerPulse

A seller-engagement assistant for solo marketplace sellers. Ask why a listing
is slipping and get a reason grounded in your own listings, reviews, sales and
stock, with every figure coming from your records and nothing sent to a buyer
without your approval.

Built as a 4-week hands-on project with Beyond Vectors. Setukart, the
marketplace in this project, is fictional, and all data is synthetic.

## Stack

Groq (`openai/gpt-oss-20b`) · LangChain · local `bge-small` embeddings · Chroma · Gradio · uv

## Status

Week 1 in progress. See `docs/tasks.md` for the plan and `docs/eval-set.md` for the test queries.

## Documents

- `docs/6-pager.md` — the case for building this
- `docs/pr-faq.md` — press release and FAQs
- `docs/team.md` — roles, stack and design decisions
- `docs/eval-set.md` — sample queries and expected agent behaviour
- `data/synthetic/README.md` — the dataset and how it was generated

## Requirements

- [uv](https://docs.astral.sh/uv/)
- A free Groq API key from console.groq.com

## Setup

```bash
git clone https://github.com/Bharat473/sellerpulse.git
cd sellerpulse
uv sync                     # creates .venv and installs exact versions from uv.lock
cp .env.example .env        # then put your Groq key in .env
uv run python scripts/check_setup.py
```

## Run

```bash
uv run python agent.py      # opens the Gradio chat on http://127.0.0.1:7860
```

## Regenerate the dataset

```bash
uv run python scripts/generate_data.py
```

## Licence

MIT
