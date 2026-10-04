# Task 9: retrieval test

- Question: Why is my Boho Wall Hanging listing underperforming?
- Seller: S001, k = 3
- Name lookup found: SKU-1001

## A. Unfiltered (no seller or SKU filter)

1. `review-REV-1024` seller S001, distance 0.257
   Review REV-1024 of "Boho Wall Hanging - Macrame" (SKU-1001), 3 stars, 8 Aug 2026: It's okay, the finish is a bit uneven.
2. `review-REV-1028` seller S001, distance 0.257
   Review REV-1028 of "Boho Wall Hanging - Macrame" (SKU-1001), 3 stars, 10 Aug 2026: Decent, but smaller than expected.
3. `review-REV-1002` seller S001, distance 0.259
   Review REV-1002 of "Boho Wall Hanging - Macrame" (SKU-1001), 3 stars, 8 Aug 2026: Decent, but smaller than expected.

## B. Filtered (seller_id = S001, sku = SKU-1001)

1. `review-REV-1024` seller S001, distance 0.257
   Review REV-1024 of "Boho Wall Hanging - Macrame" (SKU-1001), 3 stars, 8 Aug 2026: It's okay, the finish is a bit uneven.
2. `review-REV-1028` seller S001, distance 0.257
   Review REV-1028 of "Boho Wall Hanging - Macrame" (SKU-1001), 3 stars, 10 Aug 2026: Decent, but smaller than expected.
3. `review-REV-1002` seller S001, distance 0.259
   Review REV-1002 of "Boho Wall Hanging - Macrame" (SKU-1001), 3 stars, 8 Aug 2026: Decent, but smaller than expected.

## Judgment

- A: Correct. All 3 are Boho reviews explaining the problem (size, finish). Same as B, because only S001 sells this product, so this question does not test the privacy filter.
- B: Correct. Top 3 = the three 3-star Boho reviews: "smaller than expected" (x2) and "uneven finish". Weakness: REV-1028 and REV-1002 are duplicates, so only 2 distinct insights; REV-504 (price angle) missed. Week 4: try k=5 or de-duplicate.
- Settings: chunk = 1 document (no splitting), k = 3, filter = seller_id AND sku, cosine distance.
