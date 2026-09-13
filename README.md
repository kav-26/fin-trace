# Fin-Trace

**AI Financial Investigation Engine** — a multi-agent system that investigates *why* a company's financial performance changed, not just *what* changed. It plans an investigation, retrieves evidence from real filings, checks that evidence for contradictions, grounds its numbers in verified computation, and produces a cited, explainable report.

Built entirely with free tools — no paid API keys required.

---

## What it does

Ask a question like:

> "Why did Tesla's net income rise despite falling margins in 2023?"

Fin-Trace will:
1. **Plan** the investigation by breaking your question into specific sub-questions
2. **Research** each sub-question against the company's actual 10-K filing using retrieval-augmented generation (RAG)
3. **Verify** key numbers against structured financial data using real computation (Pandas), not LLM-recited figures
4. **Check for contradictions** — flags cases where different pieces of retrieved evidence disagree
5. **Synthesize** everything into a final report: a conclusion, a confidence score, key factors with cited sources, a causal reasoning chain, and an honest list of evidence gaps
6. **Visualize** the causal relationships as an interactive knowledge graph

---

## Why this isn't just a RAG chatbot

A basic RAG chatbot retrieves text and answers a question. Fin-Trace runs a genuine multi-agent investigation:

```
Question
   │
   ▼
Planner Agent ──► breaks question into sub-questions
   │
   ▼
Research Agent ──► retrieves cited evidence for each sub-question (RAG)
   │
   ▼
Contradiction Agent ──► flags disagreements across findings
   │
   ▼
Financial Analyst Agent ──► computes verified metrics from structured data (Pandas)
   │
   ▼
Reviewer Agent ──► synthesizes everything, grounds numbers in verified data,
   │                produces the final report
   ▼
Knowledge Graph ──► visualizes the causal chain
```

Orchestrated with **LangGraph** as a real state graph, not a hand-rolled sequence of function calls.

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Backend API | FastAPI | Serves the investigation pipeline as a REST API |
| Agent orchestration | LangGraph | Manages state and flow between agents |
| LLM reasoning | Groq (`openai/gpt-oss-120b`) | Free, fast inference |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) | Free, runs locally, no API key |
| Vector search | FAISS | Fast local similarity search over document chunks |
| Financial computation | Pandas | Real arithmetic for verified metrics, not LLM guesses |
| Knowledge graph | NetworkX + React Flow | Backend graph construction, interactive frontend rendering |
| History persistence | SQLite | Every investigation is saved and revisitable |
| Frontend | React + TypeScript + Vite | Multi-page dashboard |
| Styling | Tailwind CSS + shadcn/ui | Dark, dossier-style design |
| Charts | Recharts | Financial data visualization |

---

## Project structure

```
fin-trace/
├── app/
│   ├── agents/          # Planner, Contradiction, Reviewer agents
│   ├── analysis/        # Financial Analyst agent (Pandas computation)
│   ├── api/             # FastAPI backend, database, mock data
│   ├── graph/           # LangGraph workflow, knowledge graph construction
│   └── rag/             # PDF ingestion, chunking, embeddings, retrieval
├── data/
│   ├── documents/       # Source PDFs (10-K filings)
│   ├── financial/       # Structured financial data (CSV)
│   ├── index/           # FAISS vector indices (per company)
│   └── companies.json   # Active company registry
├── frontend/             # React + TypeScript dashboard
└── requirements.txt
```

---

## Setup

### Backend

```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_free_groq_api_key
```
(Get a free key at [console.groq.com/keys](https://console.groq.com/keys) — no credit card required.)

Run the backend:
```bash
uvicorn app.api.main:app
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

---

## Building your own document index

1. Place a company's 10-K PDF in `data/documents/`
2. Add an entry for it in `data/companies.json`
3. Run:
```bash
cd app/rag
python embed.py
```

---

## Validated on

- **Microsoft** (FY2023 10-K) — cloud/productivity revenue growth, margin analysis, one-time charges
- **Tesla** (FY2023 10-K) — margin compression vs. net income growth, tax benefits, capitalized stock compensation

Both produced coherent, evidence-grounded reports with correctly self-corrected numeric discrepancies — confirming the system generalizes rather than being tuned to one company.

---

## Status

Core AI pipeline (RAG, all agents, LangGraph orchestration, knowledge graph) and the full frontend dashboard (Investigate, Report, Financial Data, History, Data & Sources) are complete and working end-to-end, entirely on free infrastructure.