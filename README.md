# Agentic Equity Research Assistant

An agentic RAG system covering Infosys and TCS, combining annual report retrieval,
live news search, and structured quarterly financials — with source-cited answers
and a self-correcting retrieval loop.

Built to explore what naive RAG gets wrong (irrelevant retrievals, silent context
truncation, hallucinated confidence) and design around it.

## Architecture

User query
|
v
[Router] -- LLM classifies: docs / financials / news / multi
|
+--> [Retrieve docs] (LlamaIndex + ChromaDB, annual reports)
+--> [Retrieve financials] (SQLite, quarterly revenue/profit/EPS)
+--> [Retrieve news] (Tavily live search)
|
v
[Grade relevance] -- LLM checks: is this actually useful?
|
+-- No --> [Rewrite query] --> retry (max 1), re-routes to ORIGINAL source type
+-- Yes --> [Synthesize] -- cites which source each claim came from


Built with LangGraph for orchestration, LlamaIndex + ChromaDB for document
retrieval, Groq (`openai/gpt-oss-120b`) as the LLM backend, and local
HuggingFace embeddings (`bge-small-en-v1.5`) so ingestion has no API cost.

## What broke, and what I learned fixing it

- **PDF extraction garbage-in-garbage-out**: the default `pypdf` reader pulled
  raw PDF link/annotation objects and table-of-contents index terms into the
  vector store instead of real prose (38,248 chunks of noise). Switched to
  PyMuPDF for clean page-level text extraction (down to 1,432 real chunks).
- **Retry silently downgraded multi-source queries to single-source**: the
  rewrite-and-retry edge always routed back through document retrieval only,
  even for queries that originally needed financials + news too. Fixed by
  making the retry re-route through the *original* classified source type.
- **Blind context truncation dropped the answer**: `retrieve_multi` concatenated
  all three sources into one string, then a flat `context[:4000]` cutoff
  silently cut off the financials section (small, but exactly what a given
  query needed) because the docs section alone filled most of the budget.
  Fixed with per-source truncation budgets instead of one global cutoff.

## Eval results

8 test queries spanning all four routes (financials / docs / news / multi),
scored against known ground truth from `data/financials.db`:

| Metric | Result |
|---|---|
| Routing accuracy | 8/8 (100%) |
| Answer accuracy (correct facts present) | 8/8 (100%) |

Run it yourself: `python -m eval.run_eval`

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file with:

GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here


Add the two annual report PDFs to `data/docs/`:
- Infosys Integrated Annual Report FY26
- TCS Integrated Annual Report FY 2025-26

(Both available from investors.infosys.com and tcs.com/investor-relations.)

## Build order

```bash
python ingestion\build_financials_db.py    # SQLite financials
python ingestion\build_index.py            # PDF -> ChromaDB ingestion
python -m eval.run_eval                    # verify accuracy
streamlit run app.py                       # launch the UI
```

## Stack

LangGraph · LlamaIndex · ChromaDB · Groq · HuggingFace Embeddings · Tavily ·
SQLite · Streamlit · PyMuPDF

**Live demo:** [equity-research-assistant...streamlit.app](https://equity-research-assistant-zmcjo3av8dy4ub39qy6qju.streamlit.app/)
