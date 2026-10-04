QUESTION
Why is my Boho Wall Hanging listing underperforming?

SHOP DATA SENT TO THE LLM
[review-REV-1024] Review REV-1024 of "Boho Wall Hanging - Macrame" (SKU-1001), 3 stars, 8 Aug 2026:
It's okay, the finish is a bit uneven.

[review-REV-1028] Review REV-1028 of "Boho Wall Hanging - Macrame" (SKU-1001), 3 stars, 10 Aug 2026:
Decent, but smaller than expected.

[review-REV-1002] Review REV-1002 of "Boho Wall Hanging - Macrame" (SKU-1001), 3 stars, 8 Aug 2026:
Decent, but smaller than expected.

ANSWER
**Likely cause:** Buyers are disappointed with the product’s finish and size, leading to average 3‑star reviews that can deter new shoppers.

**Evidence:**  
- Two reviewers note the finish is uneven ([review-REV-1024]).  
- Two reviewers say the hanging is smaller than expected ([review-REV-1028], [review-REV-1002]).

**One fix:** Update the listing photos and description to show the exact dimensions and close‑up images of the finish, and add a brief note about the handcrafted nature that may cause slight variations. This sets clearer expectations and can improve future ratings and conversion.
QUESTION
How did my sales perform last week?

SHOP DATA SENT TO THE LLM
[policy-3] Setukart seller policy, section 3. Inventory & Fulfillment:
Listings must be marked out-of-stock or deactivated within 24 hours of inventory reaching zero. Sellers may not continue accepting orders for items they cannot fulfill within the stated delivery window.

[policy-2a] Setukart seller policy, section 2a. Review Guidelines: Enforcement Tiers:
Minor violation, for example a friendly reminder email asking for honest feedback: first offense, warning notice; repeat offense, warning notice.

Moderate violation, for example offering a discount code in exchange for a 5-star review: first offense, 7-day listing suspension; repeat offense, 30-day listing suspension.

Severe violation, for example paying a third party to post fake reviews: first offense, immediate listing removal; repeat offense, account termination.

[policy-2] Setukart seller policy, section 2. Review Guidelines:
Sellers may ask buyers to leave honest feedback about their order, but may not condition any discount, refund, free item, or other incentive on leaving a positive review, or on leaving any review at all.

Prohibited practices include: offering a gift card, free product, or refund in exchange for a 5-star review; asking a buyer to remove or change a negative review in exchange for compensation; posting or soliciting reviews for products the reviewer never purchased.

Violations may result in listing suspension and are reported to the marketplace trust & safety team.

ANSWER
I’m sorry, but I don’t have any sales figures for last week in the data you’ve provided, so I can’t give you a performance summary at this time. If you can share the weekly sales report or the specific numbers, I’ll be happy to help you interpret them.

## Judgment

- Run 1 (Boho): PASS on DoD. Round trip works; answer uses only the 3 retrieved reviews, cites IDs, cause → evidence → fix, ~100 words.
  Finding: "Two reviewers note the finish is uneven" — only ONE review (REV-1024) says this. The model invented a count despite Rule 1.
  Also: "average 3-star reviews" is unsupported (it saw 3 of 7 reviews), and it didn't say it can't see sales data.
  Action: add to eval set; Week 3 guardrail = code that checks every number in the answer against the Shop data. Not fixed now, to keep the baseline.
- Run 2 (sales): PASS. No figures invented; says plainly it has no sales data. Retrieval returned 3 irrelevant policy sections (no product named, nothing about sales in the corpus) — vector search always returns k results. LLM ignored them. Week 4: add a distance cutoff so far-away matches become "(no matching shop data)".
- Settings: gpt-oss-120b, temperature 0, k = 3, system prompt v5.