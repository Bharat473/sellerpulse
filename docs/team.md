# SellerPulse: Team, Roles & Stack

**Status:** Task 1 complete. Roles assigned, requirements read, stack agreed. Ready to commit once the repo exists (Task 4).
**Last updated:** 2026-09-21
**Team:** Bharat Maripi (solo build; all roles held by one person)

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
| 1 | Prompt / RAG | `prompts/`, `rag/` (corpus, chunking, embeddings, retriever) | Seller question → top-k relevant chunks + system prompt → grounded answer | Every qualitative claim traces back to a retrieved chunk; the model is told never to state numbers itself | Relevant chunk in top 3 for the test queries | A generic answer that sounds plausible but isn't about Meera's listing | 5, 7–10 |
| 2 | Tools / MCP | `tools/`, MCP server | Structured call (`seller_id`, `period` / `sku`) → exact figures or an explicit error | Numbers come only from the data; failures are reported, never hidden | 100% correct on known cases; clear error on invalid input | An invented or estimated sales or stock figure | 12–15 |
| 3 | Memory | `memory/` (schema + store) | Preference statement → stored record; new session → recalled preferences | Stored preferences are applied and never silently overridden | Session 2 recalls the session 1 preference without being asked | The agent forgetting Meera's tone, cadence or threshold | 16–17 |
| 4 | Guardrails / caching | `guardrails/`, `cache/` | Draft agent output → checked output (allowed / blocked / labelled draft); repeated query → cached result | Policy violations are refused with an alternative; customer-facing text is never published without approval | Gift request refused; every reply labelled as a draft; cache hit on a repeat query | Auto-posting a reply, or recommending review manipulation | 19–25 |
| 5 | Observability / UI | `app/` (Gradio), `observability/` | Every request → one trace (retrievals, tool calls, guardrail events) → UI + dashboard | Every step of a request is visible under one trace ID | One trace ID per request; failure rate shown on the dashboard | A black box: a wrong answer with no way to see why | 11, 18, 26–31 |
| 6 | **Data & Evals** (added) | `data/`, `evals/` | Seller interviews + sample data → synthetic dataset; expected-answers table → pass/fail scores | The system is judged against a fixed contract, not by feel | Eval pass rate on the sample queries, improving over the baseline | Shipping something that "works" but is wrong in ways nobody measured | 6, 24, 27–30 |

**Why a sixth role:** the five given roles are split by component, so nobody owns the end-to-end answer. Data & Evals fills that gap. It owns taking the agent from "it runs" to "it's reliably right".

**Where the prompt ends and the guardrail begins:** the prompt *asks* the model to behave (probabilistic). The guardrail *enforces* it in code (deterministic), for example by checking every number in the reply against tool output.

**Where effort goes:** most of my time goes to the AI parts (RAG, prompt, refusals, draft quality) because they need evals. I test the deterministic parts (tools, cache, UI) once and move on.

---

## 3. Stack (agreed)

| Layer | Choice | Reason | Alternatives considered |
|---|---|---|---|
| Language | Python | Fixed | — |
| LLM provider | **Claude (Anthropic API): Haiku for development, Sonnet for demo and evals** | Strong tool use and instruction following, which the "never invent numbers" and "drafts only" rules depend on. Same model family I already build with in Claude Code. Personal API key, separate from any subscription or employer account. Budget: about €5–10 for the whole project, with a spend limit set in the Console. All LLM calls go through one `llm.py` wrapper, so the provider can be swapped. | Rejected: OpenAI (one vendor for chat + embeddings, but no strong reason to switch); local model via Ollama (free and private, but weaker at tool use); cheaper APIs such as GPT-4o mini, DeepSeek and Gemini Flash-Lite (4–7× cheaper per question, but only about €5 saved at prototype scale) |
| Orchestration | **Raw Anthropic Python SDK** | I write the retrieval step, prompt assembly, agent loop and retries myself, in small blocks. I can see, log and explain every step, which matters for tuning quality (70%→95%) and for design reviews. | Rejected: Claude Agent SDK (runs the loop for me, so I can't see or explain it; built for file/shell agents); LangChain (heavy abstraction, hard-to-trace errors, frequent API changes); LlamaIndex (strong at retrieval, but key choices like chunk size, top-k, embedding model and prompt template come from defaults I might not know I rely on). **Checkpoint:** revisit at Task 15 (MCP). |
| Embedding model | **`BAAI/bge-small-en-v1.5`, run locally via `sentence-transformers`** (fallback: `all-MiniLM-L6-v2`) | Free, so it fits the budget. No API key, so a fresh clone runs from the README (Task 4). Trained for search on English text, which matches the corpus. Produces 384 numbers per text (about 1.5 MB for ~1,000 chunks). Sits behind one `embed()` function so it can be swapped. Task 9 (Boho chunk in the top 3) is the test. | Rejected: OpenAI embeddings and Voyage (a second vendor, key and bill; quality gain barely visible at this corpus size); keyword search (BM25) alone (misses meaning: "shipping delay" ≠ "late delivery"). **Kept in reserve:** keyword + embedding (hybrid) search as a Week 4 fix for exact codes like `SKU-1001` |
| Vector store | **Chroma (local, saved to a project folder)** | Runs with no server and persists to disk, so a fresh clone works and nothing is re-embedded on every run. **Metadata filtering** (e.g. `sku = SKU-1001`, `type = policy`, `seller_id`) keeps retrieval on the right product and document type. Simple enough to stay transparent. **Two rules:** (1) always pass my own `bge` embeddings, so Chroma's default embedding model is never used; (2) set the distance measure to cosine explicitly. A prototype choice: at 100k sellers I'd move to pgvector or a managed service. | Rejected: FAISS (very fast, but no metadata filtering or text storage; speed wasted on ~1,000 chunks); pgvector (production-grade, but needs a Postgres server, which breaks clone-and-run); plain NumPy (fully transparent, but I'd hand-build saving and filtering; kept as an optional Task 9 cross-check) |
| UI | Gradio | Fixed by Task 11 | — |
| Dev environment | VS Code + Claude Code | Already set up. Build-time tool only: it does not ship and did not decide the runtime stack | — |

Every choice above was made by comparing alternatives against the project's requirements (LLD evidence). Each is testable, not permanent: Task 9 validates the embedding model and vector store, and the Week 4 evals validate the LLM choice.

### How the pieces connect (first HLD sketch)

```
Meera (Gradio UI)
  → orchestration (my code)
      → [lookup] "Boho Wall Hanging" → SKU-1001
      → embed(question) with bge-small
      → Chroma search, filter sku=SKU-1001 → top-3 chunks
      → llm.py → Claude (system prompt + chunks + question)
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
| 6 | LLM call | System prompt + top-3 chunks + question sent to Claude through the one wrapper | `llm.py` | Task 5 |
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
| Planned (Week 4) | Cost vs quality experiment: run the same evals on Haiku, Sonnet and one cheap model (e.g. GPT-4o mini) | Turns "which model?" into evidence; matches the stretch goal of under $0.01 per query |

---

## 5. Task 1: definition of done check

| DoD item | Status | Evidence |
|---|---|---|
| Roles assigned | ✅ | Section 2: 5 required roles + Data & Evals, each written as a component contract |
| requirements.md read by everyone | ✅ | Section 1 (solo build) |
| Stack agreed | ✅ | Section 3: 4 open choices decided, alternatives recorded |
| Evidence: `docs/team.md` | ✅ drafted | Commit to the repo in Task 4 |
