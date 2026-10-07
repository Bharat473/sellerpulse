# Non-determinism investigation (Gate 3)

Question: "Why is my Boho Wall Hanging listing underperforming?" · simple/sellerpulse.py · gpt-oss-120b · temperature 0 · k = 3
Raw output of 5 runs: [nondeterminism-runs.md](nondeterminism-runs.md) · Flow: [question-trace.html](question-trace.html)

## Results (5 runs)

| What | Same in all 5? | Detail |
|---|---|---|
| Retrieved IDs and distances | Yes, 5/5 | REV-1024 (0.248), REV-1002 (0.251), REV-1028 (0.253) |
| Diagnosis (size + finish → add dimensions and close-up photos) | Yes, 5/5 | |
| "Two reviews note the finish is uneven" | Wrong in 5/5 | Only REV-1024 |
| "Three reviews say smaller than expected" | Wrong in 5/5 | Only REV-1002 and REV-1028 |
| "reduced sales" / "conversion" | 5/5 | No sales data available: unsupported |
| Wording, citation style, extra sentences | Varies | Run 4 adds "approximately X inches × Y inches" |

## Conclusion

1. Retrieval (step 13) is stable and ruled out. The issue is in step 17 (LLM).
2. Two separate problems:
   - A. Wording drifts between runs. Temperature 0 on a hosted model reduces variation but does not make output identical. Acceptable if facts stay correct.
   - B. Wrong counts appear in every run. This is a consistent bug, not randomness.

## Hypotheses for B (test one at a time)

| # | Hypothesis | Test | Result |
|---|---|---|---|
| H1 | The model does not count; it writes "two reviews say" because it sounds like evidence | Rule: never state how many reviews say something; name each by ID. Rerun 5× | (to do) |
| H2 | Duplicate review text (REV-1002 = REV-1028) inflates counts | K = 2, rerun 5× | (to do) |
| H3 | Rule 1 too narrow: "two reviews" not seen as a figure | Covered by H1 | (to do) |
| H4 | Model-specific | MODEL = openai/gpt-oss-20b, rerun 5× | (to do) |
