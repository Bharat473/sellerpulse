# SellerPulse: Team, Roles & Stack

**Status:** Task 1 complete; stack revised 2026-09-27. Roles assigned, requirements read, stack agreed. Ready to commit once the repo exists (Task 4).
**Last updated:** 2026-09-21
**Team:** Bharat Maripi and Biswajit (from 27 September; role split to agree between them)

---

## 1. Requirements confirmation

- [x] I have read `requirements.md`, including Meera Iyer's persona, the objective, the 6 sample queries, the constraints and the guardrails.

**The core rule in my own words:** *Numbers come only from tools. Text meaning comes from RAG. Preferences live in memory. Anything customer-facing stays a draft until Meera approves it.*

---

## 2. Roles

I hold every role. The roles mark the boundaries of the system: each one maps to a module in the repo, has a clear job and has one metric. When something breaks, I know which hat to put on.

Each role is written as a component contract: what module it owns, what goes in and out, what it guarantees, how I measure it, and the failure it must prevent.

| # | Role | Owns (module) | Input → Output | Guarantee | Metric | Failure it prevents | Tasks |
|---|---|---|---|---|---|---|---|
| 1 | Prompt / RAG | `prompts/`, `rag/` (corpus, chunking, embeddings, retriever) | Seller question → top-k relevant chunks + system prompt → grounded answer | Every qualitative claim traces back to a retrieved chunk **and cites its source** (e.g. `REV-504`, policy §2); the model is told never to state numbers itself. Policy text is chunked so sentences stay whole and tagged with their section, so it can be quoted exactly | Relevant chunk in top 3 for the test queries | A generic answer that sounds plausible but isn't about Meera's listing | 5, 7–10 |
| 2 | Tools / MCP | `tools/`, MCP server | Structured call (`seller_id`, `period` / `sku`) → exact figures or an explicit error | Numbers come only from the data; failures are reported, never hidden | 100% correct on known cases; clear error on invalid input | An invented or estimated sales or stock figure | 12–15 |
| 3 | Memory | `memory/` (schema + store) | Preference statement → stored record; new session → recalled preferences | Stored preferences are applied and never silently overridden | Session 2 recalls the session 1 preference without being asked | The agent forgetting Meera's tone, cadence or threshold | 16–17 |
| 4 | Guardrails / caching | `guardrails/`, `cache/` | Draft agent output → checked output (allowed / blocked / labelled draft); repeated query → cached result | Policy violations are refused with an alternative; customer-facing text is never published without approval | Gift request refused; every reply labelled as a draft; cache hit on a repeat query | Auto-posting a reply, or recommending review manipulation | 19–25 |
| 5 | Observability / UI | `app/` (Gradio), `observability/` | Every request → one trace (retrievals, tool calls, guardrail events) → UI + dashboard | Every step of a request is visible under one trace ID | One trace ID per request; failure rate shown on the dashboard | A black box: a wrong answer with no way to see why | 11, 18, 26–31 |
| 6 | **Data & Evals** (added) | `data/`, `evals/` | Seller interviews + sample data → synthetic dataset; expected-answers table → pass/fail scores | The system is judged against a fixed contract, not by feel | Eval pass rate on the sample queries, improving over the baseline | Shipping something that "works" but is wrong in ways nobody measured | 6, 24, 27–30 |

**Why a sixth role:** the five given roles are split by component, so nobody owns the end-to-end answer. Data & Evals fills that gap. It owns taking the agent from "it runs" to "it's reliably right".

**Where the prompt ends and the guardrail begins:** the prompt *asks* the model to behave (probabilistic). The guardrail *enforces* it in code (deterministic), for example by checking every number in the reply against tool output.

**Where effort goes:** most of my time goes to the AI parts (RAG, prompt, refusals, draft quality) because they need evals. I test the deterministic parts (tools, cache, UI) once and move on.

---

## 3. Stack (agreed; revised 2026-09-27)

**Change of stack:** on 27 September Abhijit, in his architect role, set the build stack for the team: Groq with an open GPT-OSS model, LangChain, `pyproject.toml` with uv, and Gradio. The original choices and their reasoning are kept in the decision log below, because the comparison is still useful evidence.

| Layer | Choice | Reason | Alternatives considered |
|---|---|---|---|
| Language | Python | Fixed | — |
| LLM | **`openai/gpt-oss-20b` on Groq** (`120b` available if quality needs it) | Set by the architect. Free tier, very fast inference, open-weight model. All calls go through one `src/llm.py` wrapper so the model or provider can be swapped | Earlier choice: Claude via the Anthropic API (stronger tool use, but a paid API). Trade-off accepted: a smaller open model, so quality has to come from retrieval and prompting, and tool calling must be tested early in Week 2 |
| Orchestration | **LangChain** (`langchain`, `langchain-groq`) | Set by the architect. Ready integrations for Groq, Chroma, HuggingFace embeddings and MCP; the team works in one framework | Earlier choice: raw Anthropic SDK, for transparency. Mitigation: keep chains small, read every line, and write retrieval filters and guardrail checks as plain Python |
| Embedding model | **`BAAI/bge-small-en-v1.5`, local** via `langchain-huggingface` | Unchanged. Groq has no embeddings API, so embeddings stay local: free, keyless, 384 numbers per text. Validated by the Task 9 top-3 test | Rejected: OpenAI embeddings and Voyage (extra vendor, key and bill); BM25 alone (misses meaning). Hybrid search kept in reserve for Week 4 |
| Vector store | **Chroma, local** via `langchain-chroma` | Unchanged. No server, persists to disk, metadata filtering by `sku`, `type` and `seller_id`. Always pass our own embeddings; set cosine distance explicitly | Rejected: FAISS (no metadata filtering), pgvector (needs a server), plain NumPy (kept as an optional cross-check) |
| Packaging | **uv + `pyproject.toml` + `uv.lock`** | Set by the architect. `uv sync` reproduces the exact environment from the lock file, which `requirements.txt` with `>=` does not | Earlier: venv + pip + `requirements.txt` |
| UI | Gradio | Fixed by Task 11 | — |
| Code size | Keep each file minimal (under about 60 lines) | Architect's rule: small enough to read and explain line by line | — |
| Dev environment | VS Code + Claude Code | Build-time tool only; it does not ship | — |
| Secrets | `GROQ_API_KEY` in `.env` (git-ignored); `.env.example` shows the variable only | Keys never enter the repo | — |

### How the pieces connect (first HLD sketch)

```
Meera (Gradio UI)
  → orchestration (my code)
      → [lookup] "Boho Wall Hanging" → SKU-1001
      → embed(question) with bge-small
      → Chroma search, filter sku=SKU-1001 → top-3 chunks
      → llm.py → gpt-oss on Groq via LangChain (system prompt + chunks + question)
            ↺ [Week 2] Claude asks for a tool → my code runs it → result back to Claude
            ↺ [Week 2] memory: Meera's preferences added to the prompt
      → answer (drafts labelled, every step logged)
  → back to Meera
```

| # | Step | What happens (Boho example) | Planned file | Built in |
|---|---|---|---|---|
| 1 | Gradio UI | Meera types the question in the browser | `app.py` | Task 11 |
| 2 | Orchestration | My code runs the steps below in order | `agent.py` | Task 10 |
| 3 | Listing lookup | Turns "Boho Wall Hanging" into `SKU-1001` using the listings table. Ambiguous names are the Task 32 edge case | `rag/lookup.py` | Task 9–10 |
| 4 | Embed | `bge-small` turns the question into 384 numbers | `rag/embed.py` | Task 8 |
| 5 | Retrieve | Chroma returns the nearest chunks, filtered to `sku = SKU-1001` | `rag/retrieve.py` | Task 9 |
| 6 | LLM call | System prompt + top-3 chunks + question sent to the model through the one wrapper | `llm.py` | Task 5 |
| 7 | Tool loop (↺) | Claude *asks* for a tool (e.g. stock level); it can't run it itself, so my code runs it and sends the result back. Repeats until Claude writes the final answer | `tools/`, `agent.py` | Week 2 |
| 8 | Memory (↺) | Meera's stored preferences (tone, cadence, threshold) are added to the prompt | `memory/` | Week 2 |
| 9 | Answer | Grounded diagnosis; drafts labelled; each step logged | — | Week 1 basic; Weeks 3–4 full |

**Week 1 demo scope:** every step except the ↺ lines (no tools, memory or guardrails yet).

**Why the tool step is a loop, not an arrow:** Claude decides *whether* it needs data and *which* tool to call; my code does the actual work. That loop is the core of an agent and the main build in Week 2.

---

## 4. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-09-21 | Keep the 5 given roles and add Data & Evals | Nobody owned end-to-end quality |
| 2026-09-21 | LLM = Claude via the Anthropic API | Tool use and instruction following suit the guardrail rules. Trade-off: Anthropic has no embeddings model, so a second provider is needed for embeddings |
| 2026-09-21 | Orchestration = raw Anthropic SDK | Transparency: I make and can explain every retrieval and loop decision. Trade-off: more code to write myself |
| 2026-09-21 | Budget: about €5–10 total; Haiku for dev, Sonnet for demo | Cost only matters at scale. Quality first, then test cheaper models with evals |
| 2026-09-21 | All LLM calls go through one `llm.py` wrapper | The raw SDK ties the code to Anthropic; the wrapper keeps the provider swappable |
| 2026-09-21 | Keep build-time tooling (Claude Code) separate from runtime choices | The runtime stack is chosen on requirements, not on which tool I code with |
| 2026-09-21 | Embeddings = `bge-small-en-v1.5`, local | Free, keyless and good at search. Same model for documents and questions; swappable behind `embed()`; to be validated by the Task 9 top-3 test |
| 2026-09-21 | Added a listing-lookup step before retrieval; drew the tool step as a loop with Claude | Metadata filtering needs the SKU first; tools run in a loop that Claude drives, not as a final step |
| 2026-09-21 | Vector store = Chroma (local) | No server, persists to disk, metadata filtering. Always pass my own embeddings; cosine distance set explicitly |
| 2026-09-22 | Answers cite their sources; policy chunks keep sentences whole | Found by mapping 6-pager §4 capabilities to components: "points to the review it relied on" and "quotes the policy line" had no owner |
| 2026-09-27 | Stack changed to Groq (`gpt-oss-20b`) + LangChain + uv/pyproject + Gradio | Set by Abhijit in the architect role for the team. Embeddings and vector store unchanged. Accepted trade-offs: weaker tool calling than a frontier model, and less visibility inside LangChain chains |
| 2026-09-27 | Team is now two: Bharat and Biswajit | One shared 6-pager and PR/FAQ, agreed by both |
| Planned (Week 4) | Model comparison: run the same evals on `gpt-oss-20b` and `gpt-oss-120b` | Turns "which model?" into evidence: score against latency and free-tier usage |

---

## 5. Task 1: definition of done check

| DoD item | Status | Evidence |
|---|---|---|
| Roles assigned | ✅ | Section 2: 5 required roles + Data & Evals, each written as a component contract |
| requirements.md read by everyone | ✅ | Section 1 (solo build) |
| Stack agreed | ✅ | Section 3: 4 open choices decided, alternatives recorded |
| Evidence: `docs/team.md` | ✅ drafted | Commit to the repo in Task 4 |
