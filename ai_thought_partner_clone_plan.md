# AI Thought‑Partner Clone — Build & Training Plan

A practical blueprint to build your private “AI thought‑partner clone” that knows your business, thinks in your style, and improves from your feedback.

---

## Table of Contents
1. [What You’re Building](#what-youre-building)
2. [Phase 1 — MVP (This Week)](#phase-1--mvp-this-week)
   - [1) Persona & Operating Rules](#1-persona--operating-rules)
   - [2) Ingest Knowledge (RAG)](#2-ingest-knowledge-rag)
   - [3) Give It Tools (Hands)](#3-give-it-tools-hands)
   - [4) Agent Loop (Reliable & Simple)](#4-agent-loop-reliable--simple)
   - [5) UI, Logging & Deployments](#5-ui-logging--deployments)
3. [Phase 2 — Make It Think Like You (Training)](#phase-2--make-it-think-like-you-training)
   - [A) Build a Personal Dataset](#a-build-a-personal-dataset)
   - [B) Fine‑Tuning Strategy (Optional)](#b-fine-tuning-strategy-optional)
   - [C) Evals You’ll Actually Use](#c-evals-youll-actually-use)
4. [Phase 3 — Memory & Growth](#phase-3--memory--growth)
5. [Security & Governance](#security--governance)
6. [What to Build First (1–2 Days)](#what-to-build-first-12-days)
7. [Training Roadmap (Weeks 2–4)](#training-roadmap-weeks-2–4)
8. [Data You Should Seed](#data-you-should-seed)
9. [Ready‑to‑Use File Templates](#ready-to-use-file-templates)
10. [How You’ll Train It Day‑to‑Day](#how-youll-train-it-day-to-day)
11. [Appendix A — Minimal Agent Skeleton (Python)](#appendix-a--minimal-agent-skeleton-python)
12. [Appendix B — Example Persona Prompt](#appendix-b--example-persona-prompt)
13. [Appendix C — Example Config](#appendix-c--example-config)
14. [Appendix D — Evaluation Rubric](#appendix-d--evaluation-rubric)

---

## What You’re Building

A private agent that:
- **Thinks like you** (tone, values, decision heuristics).
- **Knows what you know** (docs, code, SOPs, notes).
- **Can act** via tools (search, Trello, Gmail/Calendar read, GitHub, spreadsheets).
- **Improves over time** from your feedback.

You can ship a strong MVP **without fine‑tuning** (RAG + tools + persona). Add lightweight training (LoRA/DPO) later to mirror your judgment more closely.

---

## Phase 1 — MVP (This Week)

### 1) Persona & Operating Rules

Create `system_prompt.md` with your tone, heuristics, and operating rules (see [Appendix B](#appendix-b--example-persona-prompt)).

**Tips**
- Explicitly list decision heuristics.
- State escalation rules (ethics/safety).
- Define response style (bullets > walls of text).
- Add bilingual behavior if you want ES/EN responses.

---

### 2) Ingest Knowledge (RAG)

**Collect**
- Proposals, SOWs, SOPs, deliverables, code READMEs, Trello exports, meeting notes, blog drafts, pitch decks.

**Chunking**
- 700–1200 tokens per chunk, keep headings and local anchors.
- Preserve metadata: `source`, `date`, `owner`, `doc_type`, `project`.

**Index**
- Use FAISS/Chroma/pgvector/Qdrant with OpenAI/Instructor/E5 embeddings (or your preferred local embeddings).
- Keep a small **keyword index** (SQLite FTS) for exact IDs/names.

**Retrieval**
- Hybrid: vector search + keyword re‑rank.
- Pass 3–7 top chunks into the model with citations/links.

---

### 3) Give It Tools (Hands)

Start with read/search tools you’ll use daily:
- **Docs search** (your RAG index).
- **Browser** (public facts).
- **Trello** (create tasks; read lists/cards).
- **Calendar/Gmail read** (summaries, “what matters today?”).
- **GitHub** (PR summary, TODO extraction).
- **CSV/Sheets** (light analysis).

Wire each tool with strict, typed I/O and **idempotent** operations. Require explicit confirmation on write actions.

---

### 4) Agent Loop (Reliable & Simple)

- **Model**: local (Ollama/LM Studio) or API for stronger reasoning.
- **Orchestrator**: a small loop with tool selection, retrieval, scratchpad, final answer.
- **Memory**: 
  - Short‑term per chat.
  - Long‑term profile facts (SQLite/JSON) via a `get_profile` tool.

A minimal Python skeleton is in [Appendix A](#appendix-a--minimal-agent-skeleton-python).

---

### 5) UI, Logging & Deployments

- **CLI** for yourself; **Slack bot** for quick access.
- Optional web chat (FastAPI + small React/Next page).
- **Logging**: prompts, retrieved chunks, tools chosen, response, and your 👍/👎 with reason.
- Store logs for improvement and training data mining.

---

## Phase 2 — Make It Think Like You (Training)

Start **without** fine‑tuning. If after 1–2 weeks you want tighter alignment:

### A) Build a Personal Dataset

1) **Persona set** (50–100 items): your writing samples → “rewrite in my voice” or “critique using my heuristics.”

Format (JSONL):

```json
{"prompt":"Draft a 1-paragraph client update about X.","context":"<snippets or N/A>","output":"<your gold response>"}
```

2) **Decision heuristics set** (30–60): mini‑cases → “Given A/B/C, what do you choose and why?” Provide bullet reasoning.

3) **Critique set** (30–60): give weak drafts; your **line edits** + “why” notes become targets.

4) **Preference pairs** (DPO/ORPO) (200–1000 pairs over time): log two candidate answers; you mark the preferred.

### B) Fine‑Tuning Strategy (Optional)

- **SFT via LoRA/QLoRA** on persona/critique/heuristics (style, structure, judgment).
- **Preference pass** (DPO/ORPO) using the pairwise choices.
- Keep facts in RAG; train **judgment/tone**, not knowledge.
- Re‑run evals; keep changes if scores improve.

### C) Evals You’ll Actually Use

A “golden set” (25–50 prompts) you care about:
- Exec summaries, experiment critiques, client emails, scope clarifications.

Score **clarity, correctness, tone, actionability** (1–5). Track before/after training.

---

## Phase 3 — Memory & Growth

**Long‑term memory schema (SQLite/JSON)**

`facts(key, value, source, first_seen, last_used, confidence)`

Examples:
- `("client_pref_report_day","Friday","calendar",...)`
- `("brand_tone","concise-candid-optimistic-tech","persona",...)`

Add a “**remember this**” command. Surface facts via a `get_profile` tool and show which facts were used (“memory transparency”).

**Feedback loop**
- Every response gets 👍/👎 with reason → stored as preference data.
- Nightly: re‑index new docs; generate concise summaries for large docs (improves retrieval).

---

## Security & Governance

- Separate indices for private vs shareable projects.
- Red‑team evals: “Should we email client’s raw data?” → expect “No, and why.”
- Log all tool calls; require explicit confirmation for write actions (emailing, Trello creates).
- Access control per project/client if others will use the agent.

---

## What to Build First (1–2 Days)

- [ ] `system_prompt.md` (persona).
- [ ] RAG index over core docs.
- [ ] Agent loop with 3 tools: `search_docs`, `get_profile`, `trello_create`.
- [ ] CLI and Slack bot.
- [ ] Logging + thumbs feedback.

This already delivers a strong “thought‑partner” effect.

---

## Training Roadmap (Weeks 2–4)

- **Week 2**: Collect 100–200 gold outputs from real work (your edits become gold).
- **Week 3**: First **LoRA SFT**; re‑run evals.
- **Week 4**: Add 300–500 preference pairs; run **DPO**; re‑run evals; lock persona.

---

## Data You Should Seed

- Company mission, offers, pricing, ICP, objections, positioning.
- Proposal templates, past SOWs/NDAs/SLAs.
- Meeting notes & weekly updates (short summaries best for RAG).
- Trello/roadmap labels and tag definitions.
- Writing samples (emails, reports, posts) that represent your voice.

---

## Ready‑to‑Use File Templates

```
/ai-clone/
  system_prompt.md          # persona (Appendix B sample)
  config.yaml               # model, vector DB, tool keys (Appendix C sample)
  data/
    sft.jsonl               # (prompt, context, output) for SFT
    prefs.jsonl             # DPO pairs: {prompt, chosen, rejected}
  evals/
    golden.jsonl            # 25–50 prompts + gold answers
  logs/
    chat_logs.jsonl         # prompts, retrieved chunks, tools, feedback
```

---

## How You’ll Train It Day‑to‑Day

- Use it for real work. When it drafts, **edit in place** → your edits become gold data.
- Give short, pointed feedback (“too wordy”, “missed risk X”). Capture tags automatically.
- Weekly “**clone review**”: sample 10 chats, file 5 improvements (persona, tools, or RAG).

---

## Appendix A — Minimal Agent Skeleton (Python)

```python
# pip install fastapi uvicorn pydantic faiss-cpu chromadb tiktoken
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# --- Tools (stubs you’ll fill) ---
def search_docs(query: str, k: int = 5) -> List[Dict[str, Any]]:
    # return [{"text": "...", "source": "...", "metadata": {...}}, ...]
    ...

def web_search(query: str) -> str: ...
def trello_create(card_title: str, list_id: str) -> str: ...
def get_profile() -> Dict[str, Any]: ...   # your long-term memory store

# --- Tool registry ---
TOOLS = {
    "search_docs": {"fn": search_docs, "schema": {"query": str, "k": int}},
    "web_search": {"fn": web_search, "schema": {"query": str}},
    "trello_create": {"fn": trello_create, "schema": {"card_title": str, "list_id": str}},
    "get_profile": {"fn": get_profile, "schema": {}},
}

SYSTEM_PROMPT = open("system_prompt.md").read()

def call_llm(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    # drop-in for OpenAI/Ollama/LM Studio; return dict with either:
    # {"content": "..."} or {"tool_call": {"name": "...", "args": {...}}}
    ...

def agent(query: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}]
    scratch = []

    for _ in range(6):  # small, bounded reasoning
        resp = call_llm(messages + ([{"role":"system","content":"Scratch:"+str(scratch)}] if scratch else []))
        if "tool_call" in resp:
            name = resp["tool_call"]["name"]
            args = resp["tool_call"]["args"]
            out = TOOLS[name]["fn"](**args)
            scratch.append({"tool": name, "args": args, "output": out})
            messages.append({"role":"tool","content": f"{name}=>{out}"})
            continue
        return resp["content"]
    return "Loop limit reached—try rephrasing or splitting the request."
```

---

## Appendix B — Example Persona Prompt

```markdown
You are ANDY-CLONE, my thought partner for Dills Analytics.
Goals: (1) speed my decisions; (2) reduce errors; (3) draft, critique, and plan.
Voice: concise, candid, optimistic, technically rigorous.
When uncertain: say so; propose 2–3 options with tradeoffs.
Biases to emulate:
- Favor verifiable math / experiments over vibes.
- Prefer incremental, testable changes.
- Default to Python-first, GPU-aware thinking for ML.
Decision heuristics:
- If change affects safety/ethics → escalate.
- If a task < 15 min → suggest doing now or automating.
- If tooling choice is unclear → pick the simplest that works, explain why.
Style rules:
- Bullet points > walls of text.
- Include quick checklists and next steps.
- If Spanish appears, respond bilingually (ES/EN).
```

---

## Appendix C — Example Config

```yaml
model:
  backend: "openai|ollama|lmstudio"
  name: "gpt-4.1|llama-3.1-70b|mixtral-8x7b"
  temperature: 0.3
  max_tokens: 1200

rag:
  db: "faiss|chroma|pgvector|qdrant"
  embedding_model: "text-embedding-3-large|e5-large"
  chunk_tokens: 900
  top_k: 6
  rerank: true

tools:
  trello:
    enabled: true
    list_id: "YOUR_LIST_ID"
  browser:
    enabled: true
  gmail_read:
    enabled: true
  calendar_read:
    enabled: true

logging:
  path: "./logs/chat_logs.jsonl"
  capture_feedback: true
```

---

## Appendix D — Evaluation Rubric

Score each response 1–5 on:
- **Clarity**: direct, structured, avoids fluff.
- **Correctness**: factual, math/logic checks out.
- **Tone**: matches persona; client‑appropriate.
- **Actionability**: concrete next steps, decisions, or checklists.

Track mean score per dimension over time; only keep training changes that improve scores.
