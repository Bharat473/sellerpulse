# SellerPulse: 4-Week Task Plan (working copy)

*Abhijit's task list, definitions of done and evidence are unchanged. This copy adds a **Stack note** to each task showing how it is built with the chosen stack. The original file is kept alongside as `docs/tasks-original.md`.*

## Chosen stack (updated 2026-09-29)

| Layer | Choice | Note |
|---|---|---|
| LLM | `openai/gpt-oss-20b` on **Groq** | Free tier: roughly 30 requests/min, 14,400/day, per-model token limits; limits are per organisation, so extra keys do not raise them |
| Orchestration | **LangChain** | `langchain`, `langchain-groq`; chains for RAG, agents for tools in Week 2 |
| Embeddings | `BAAI/bge-small-en-v1.5` locally via `langchain-huggingface` + `sentence-transformers` | Groq has **no embeddings API**, so embeddings stay local. 384 numbers per chunk |
| Vector store | **Chroma** via `langchain-chroma` | Local, persists to disk, metadata filtering by `sku` / `type` / `seller_id` |
| Packaging | **uv** + `pyproject.toml` + `uv.lock` | Replaces venv + requirements.txt. `uv sync` recreates the exact environment |
| UI | **Gradio** | Local demo, as required by Task 11 |
| Env | `GROQ_API_KEY` in `.env` (git-ignored) | `.env.example` shows the variable without the key |

---

## Week 1: Foundations, RAG & UI (11 tasks)
**Demo Goal:** A live Gradio chat UI that answers a seller's performance question with a RAG-grounded diagnosis of a specific listing; no tools, memory, or guardrails yet, but it's clickable and shareable. Plus two written deliverables: an Amazon-style 6-pager and a PR/FAQ.

| # | Task (~1 hr) | Definition of Done | Evidence of Completion | Stack note |
|---|---|---|---|---|
| 1 | Kickoff: assign roles, review requirements.md and Meera Iyer's persona/objective, agree on tech stack | Roles assigned (prompt/RAG, tools/MCP, memory, guardrails/caching, observability/UI owners); requirements.md read by everyone; stack agreed | A `docs/team.md` listing roles and stack, with each member confirming they've read requirements.md | Update `docs/team.md` stack table and decision log to Groq + LangChain + uv, with the alternatives rejected and why |
| 2 | Write an Amazon-style 6-pager for SellerPulse | 6-pager committed as a narrative document; every section present and specific to SellerPulse | `docs/6-pager.md`, reviewed | Unaffected by the stack. Check the cost line still holds on Groq's free tier |
| 3 | Write a PR/FAQ for SellerPulse | PR/FAQ committed; press release from Meera's point of view; at least 5 FAQs including one on data handling and one on guardrails | `docs/pr-faq.md`, reviewed | Unaffected by the stack |
| 4 | Set up the git repository | Repo exists remotely with main + feature branches; README lets a fresh clone run the project | A teammate clones the repo and runs it successfully from README alone | README setup becomes `uv sync` then `uv run python scripts/check_setup.py`. Delete `requirements.txt`; commit `pyproject.toml` **and** `uv.lock`. `check_setup.py` checks `GROQ_API_KEY` (prefix `gsk_`) and imports `langchain`, `langchain_groq`, `langchain_chroma`, `langchain_huggingface`, `gradio`, `pandas` |
| 5 | Draft the system prompt: seller-engagement tone, "never invent a number" rule, draft-only output rule | Prompt file committed; 2 manual test prompts confirm figures are only ever tool-sourced and outputs are labeled as drafts | Prompt file in repo + pasted transcript of the 2 test runs | Prompt lives in `src/prompts/system.md`, loaded into a LangChain `ChatPromptTemplate`. Model called through `ChatGroq(model="openai/gpt-oss-20b")`, wrapped in `src/llm.py` so the provider stays swappable. In Week 1 the correct behaviour is to **refuse to state numbers**, since no tools exist yet |
| 6 | Generate a synthetic dataset of listings, sales history, inventory levels, orders and reviews | Dataset file committed covering ~150 SKUs with several weeks of sales/order history | Dataset file in repo + a summary count of listings/orders/reviews | pandas + openpyxl. Keep Abhijit's original 10 SKUs unchanged and build around them; seed the awkward cases (missing reviews, ambiguous names, active-but-out-of-stock listing) |
| 7 | Prepare the RAG corpus: listing content, past reviews, marketplace seller-policy documents | Corpus covers all 6 sample queries, especially the underperforming-listing diagnosis and the policy-violation case | Corpus files committed with item/document count | Write listing descriptions (the sample data has titles only). Policy text chunked so sentences stay whole and each chunk carries its section, so rules can be quoted exactly |
| 8 | Build the ingestion pipeline: chunk and embed the corpus into a vector store | Pipeline runs with no errors; vector store has the expected chunk count | Console log showing chunk/embedding count | LangChain `RecursiveCharacterTextSplitter` → `HuggingFaceEmbeddings("BAAI/bge-small-en-v1.5")` → `Chroma.from_documents(persist_directory=".chroma")`. Attach metadata (`sku`, `type`, `date`, `review_id`) at this step; retrieval quality depends on it |
| 9 | Implement retrieval and test against "why is my Boho Wall Hanging listing underperforming?" | Relevant listing/review chunk(s) appear in the top-3 retrieved results | Logged query + retrieved chunks with a correct/incorrect judgment | `vectorstore.as_retriever(search_kwargs={"k": 3, "filter": {"sku": "SKU-1001"}})`. Needs a name→SKU lookup first. Record the chunk size, k and filter you chose and why |
| 10 | Wire a minimal prototype: seller question → grounded diagnosis (no tools yet) | Full query→diagnosis round trip runs without crashing and reflects the corpus data | Terminal/notebook transcript of one successful run | A LangChain chain: retriever → prompt → `ChatGroq` → output parser. Keep it under ~50 lines and be able to explain each step |
| 11 | Build a Gradio chat UI and run it locally with a shareable link | Gradio app launches and returns a grounded diagnosis for a real query | Screenshot of the running UI + shareable link posted to the team channel | `gr.ChatInterface` calling the Week 1 chain. `demo.launch(share=True)` gives a temporary public link |

## Week 2: Tools, MCP & Memory (7 tasks)
**Demo Goal:** The same Gradio UI now pulls live sales/inventory figures and drafts a review reply, and remembers the seller's notification preferences across two visits.

| # | Task (~1 hr) | Definition of Done | Evidence of Completion | Stack note |
|---|---|---|---|---|
| 12 | Design tool specs: `get_sales_analytics(seller_id, period)` and `check_inventory_status(sku)` | Written spec for both tools: inputs, outputs, error cases | `docs/tools.md` with both signatures and example input/output | Spec first, code second. Define the error shape now: what the tool returns when the SKU is unknown or the period is invalid |
| 13 | Implement the sales-analytics tool | Returns correct revenue/units/orders for a known period and a clear error for an invalid one | Test log showing both cases | LangChain `@tool` decorator over a pandas function. Compute in pandas, never in the model |
| 14 | Implement the inventory-status tool | Returns correct stock level for a known SKU and a clear error for an unknown one | Test log showing both cases | Same pattern. Return structured data, not prose |
| 15 | Set up MCP to expose both tools to the agent; test a full round trip | Agent calls both tools via MCP and uses their results in a live response | Trace/log of one query showing the response built from tool output | Run the tools as a small MCP server and connect with `langchain-mcp-adapters`. Confirm `gpt-oss-20b` on Groq handles tool calling reliably; if not, note it and fall back to LangChain tools directly, recording the reason |
| 16 | Design the memory schema: notification cadence, reply tone, restock threshold | Schema documented; a record can be written and read back correctly | Schema doc + log of one record written and retrieved | A JSON file keyed by `seller_id` is enough. Keep it separate from chat history |
| 17 | Integrate memory; test preference recall across 2 sessions | Preference stated in session 1 is correctly recalled, unprompted, in session 2 | Transcripts of both sessions showing the preference and its recall | Load preferences into the system prompt at the start of each session. Demo by restarting the app between the two sessions |
| 18 | Wire tools and memory into the Gradio UI via an expandable "agent trace" panel | Panel lists each tool call and the recalled preferences for the response | Screenshot of the panel expanded on a real query | A LangChain callback handler collects tool calls; render them in a `gr.Accordion` |

## Week 3: Guardrails & Caching (7 tasks)
**Demo Goal:** In the live UI, show the agent refuse a review-manipulation request and label a review-reply draft as pending approval, and show a visible speed-up (cache hit badge) on a repeated analytics query.

| # | Task (~1 hr) | Definition of Done | Evidence of Completion | Stack note |
|---|---|---|---|---|
| 19 | Codify guardrail rules: no fabricated figures, no auto-publishing, no policy-violating recommendations | Rules written as a checklist mapped to requirements.md's guardrail section | `docs/guardrails.md` with each rule and its requirements.md reference | Plain document. Each rule needs a test in Task 21 |
| 20 | Implement guardrail checks verified against live tool output and the policy corpus | Every figure and every customer-facing draft passes through the guardrail check before reaching the user | Log entry showing an output being labeled/filtered by the guardrail layer | Write these as **plain Python after the chain**, not as prompt instructions: extract numbers from the answer and compare against tool output; force the draft label. Deterministic code, not a second model call |
| 21 | Test guardrails against the "free gift for a 5-star review" request and a review-reply draft | Policy violation is correctly refused with an explanation and alternative; review reply is correctly labeled as a draft awaiting approval | Transcripts of both test runs | Also test three reworded versions of the gift request. Keep the list and extend it whenever one gets through |
| 22 | Implement caching for RAG embeddings and frequent analytics queries | Repeated identical queries hit the cache instead of re-querying | Log showing a cache miss then a cache hit on the repeat | LangChain `set_llm_cache(SQLiteCache(...))` for model calls; `CacheBackedEmbeddings` for embeddings |
| 23 | Measure cache hit rate and latency improvement | Latency compared for cached vs. uncached calls with documented improvement | Before/after latency numbers committed to the repo | Groq is very fast already, so expect the saving to be smaller than on a slower provider. Report the honest number |
| 24 | Run all 6 sample queries end-to-end; fix bugs | All 6 run and are compared against the expected-answers table | Filled-in expected-answers table with actual output and pass/fail per row | Watch the free-tier rate limit while looping over queries |
| 25 | Surface guardrail status, draft-approval state and cache hit/miss as badges in the Gradio UI | UI visibly shows guardrail blocks, draft-pending labels and cache hits | Screenshots showing all three badge states | Return badge state from the chain alongside the answer and render it in Gradio |

## Week 4: Observability, Evals & Demo Readiness (9 tasks)
**Demo Goal:** Full live walkthrough: Gradio UI + observability dashboard, an eval score shown before/after your error-analysis fixes, and a policy-violation refusal on demand.

| # | Task (~1 hr) | Definition of Done | Evidence of Completion | Stack note |
|---|---|---|---|---|
| 26 | Instrument observability: log retrievals, tool calls, guardrail triggers and tool failures | Every event for one request shares a single trace ID | Exported trace for one request showing all event types tied together | A custom LangChain callback handler writing JSON lines with one trace ID per request. LangSmith is optional and needs an account; a local log keeps the demo self-contained |
| 27 | Build an eval harness from the expected-answers table with pass/fail scoring | Each of the 6 rows is an automated test case with a scorer | Eval script committed, runnable with one command | Plain Python (or pytest) over the chain. `uv run python evals/run.py` |
| 28 | Run the eval suite against the synthetic seller data; record baseline scores | Suite runs successfully and produces a baseline score | Saved baseline report (score, timestamp, per-case pass/fail) | Record which model produced the baseline, since Groq can change model availability |
| 29 | Do error analysis: categorize failures, find root causes, pick top 3 fixes | Every failing case categorized (retrieval miss, tool error, guardrail miss, fabricated figure, latency) with a root cause and prioritized fix | Error-analysis table committed | This is the 70%→95% work. Expect most misses to be retrieval, not the model |
| 30 | Apply the top fixes and re-run the eval suite; record the improvement | Score improves measurably over baseline after the fixes | Before/after eval report showing the score delta | Typical fixes: chunk size, k, metadata filter, prompt wording |
| 31 | Build a dashboard: tool-call failure rate, draft-approval turnaround, guardrail trigger count | Dashboard shows real data and is reachable from the UI | Screenshot/link of the live dashboard with real run data | A second Gradio tab reading the trace log |
| 32 | Handle edge cases: analytics API timeout, ambiguous listing references, no catalog/review match | Each edge case produces a graceful fallback instead of a crash | Log/transcript of each edge case being triggered and handled | Add a fourth: **Groq rate-limit (HTTP 429)**, which the free tier makes likely during a demo. Retry with backoff, then fall back to the last confirmed data |
| 33 | Prepare the demo script: Meera persona, 2-3 live queries, a memory demo, the scorecard | Script covers all elements and is timed to the demo slot | Script document + timed rehearsal note | Rehearse with the rate limit in mind: do not loop queries just before the demo |
| 34 | Final rehearsal, deploy the demo build, record a backup demo video | Live demo runs end-to-end without failure; build deployed and reachable; backup video exists | Deployment link + backup video link, both in README | Local Gradio is enough per Abhijit; the backup video covers a failed live call |

## Stretch Goals (optional)
- Baseline comparison: the same requests through a vanilla LLM with no RAG/tools/guardrails, side by side.
- Red-team your own agent: try to get it to auto-publish or recommend a policy-violating tactic, then harden against what worked.
- Proactive "morning brief" summarising overnight orders, low stock and new reviews.
- Latency/cost budget (e.g. under 3s, under $0.01/query) with before/after numbers. On Groq's free tier, report requests used rather than money.
- Model comparison on the eval suite: `gpt-oss-20b` versus a larger Groq model, score against latency.
