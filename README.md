# SellerPulse

A seller-engagement assistant for solo marketplace sellers. Ask why a listing
is slipping and get a reason grounded in your own listings, reviews, sales and
stock, with every figure coming from your records and nothing sent to a buyer
without your approval.

Built as a 4-week hands-on project with Beyond Vectors. Setukart, the
marketplace in this project, is fictional, and all data is synthetic.

## Status

Week 1 in progress. See `docs/tasks.md` for the plan.

## Documents

- `docs/6-pager.md` — the case for building this
- `docs/pr-faq.md` — press release and FAQs
- `docs/team.md` — roles, stack and design decisions

## Requirements

- Python 3.11 or newer
- An Anthropic API key

## Setup

```bash
git clone https://github.com/<your-username>/sellerpulse.git
cd sellerpulse
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then put your API key in .env
python scripts/check_setup.py
```

## Licence

MIT
