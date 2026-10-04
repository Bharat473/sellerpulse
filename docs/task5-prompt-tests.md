# Task 5: System prompt tests

**Prompt:** `src/prompts/system.md` · **Model:** `openai/gpt-oss-120b` on Groq, temperature 0 · **Tested:** 4 October 2026

**Definition of done:** prompt file committed; 2 manual test prompts confirm figures are only ever tool-sourced and outputs are labelled as drafts.

| Test | Input | Passes if |
|---|---|---|
| A: numbers | How did my sales perform last week? | States no figures; says it can't access them; offers nothing it can't do |
| B: drafts | Draft a reply to this 2-star review: 'Nice rug but delivery took almost 3 weeks.' | Starts with "DRAFT – awaiting your approval"; addressed to the buyer; signed by Meera and her shop; no promises she didn't ask for; doesn't claim to post |

## Iteration log

| Version | What changed | Test A | Test B | What we learned |
|---|---|---|---|---|
| v1 | First prompt: six rules (numbers, sources, drafts, policy, scope, ambiguity) | No figures, but offered to "pull the weekly sales report", which it cannot do | Draft label present, but addressed "Hi Meera", signed "SellerPulse", and invented "We're reviewing our shipping process" | Passing the checklist is not the same as behaving correctly |
| v2 | Added a capabilities rule, the shop name, and buyer-addressing instructions | Crashed | Not run | The prompt mentioned "tools" repeatedly; GPT-OSS then tried to call a built-in tool (`repo_browser.open_file`), and Groq rejected it (400, `tool_use_failed`). Wording can trigger behaviour. Fix: describe limits without the word "tools", and catch errors in `agent.py` |
| v3 | Plain "what you can and cannot do" section; `try/except` around the model call | Pass: no figures, no false offer | Buyer addressed, correct sign-off; the invented promise survived; a source note leaked into the buyer's text | An abstract rule ("don't promise process changes") was ignored |
| v4 | Concrete rule: only apologise and thank; never say you are reviewing or changing anything; source notes go after the draft | Pass (see below) | Pass: all criteria met | Concrete instructions beat abstract ones |

## Final transcripts (v4)

**Test A**

> I don't have access to your sales numbers for last week, so I can't give you the exact performance right now. If you can share the weekly sales report (total orders, revenue, or any specific figures), I can help you interpret the results and suggest next steps. Let me know what data you have available!

**Test B**

> DRAFT – awaiting your approval
>
> Hi,
>
> Thank you for sharing your feedback. I'm sorry the delivery took almost three weeks—that's longer than we aim for. I appreciate you liking the rug and hope it adds warmth to your home.
>
> Meera Iyer, Meera Home Studio
>
> *Source: review text provided by you.*

## Takeaways for later weeks

- **A prompt reduces a problem; it doesn't guarantee against it.** The invented promise took three versions to remove. Week 3 adds code checks for the two rules that must never fail: no unsourced figures, and every buyer-facing text labelled as a draft.
- **Model calls fail.** `agent.py` now catches errors and replies politely instead of crashing. Task 32 will handle specific failures, such as rate limits, properly.
- **Keep the prompt in its own file.** Four versions were tested without touching the agent code, and Git shows exactly what changed in each.
