# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Instructions

Never use the "Co-authored by Claude" line always refrain from using any means that show claude/ ai-assisted agents were used

## Project Overview

**Seagull** is a collaborative research intelligence platform centered on **claim-level verification** against uploaded PDFs. Users can audit factual claims with scored evidence, run RAG chat over research papers, and explore an auto-generated knowledge graph — all within shared, real-time workspaces.

## Commands

### Backend (FastAPI + Python)

```bash
cd backend
source venv/bin/activate            # Windows: venv\Scripts\activate

uvicorn app.main:app --reload --port 8000   # Dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4  # Production

pytest -v tests/                    # All tests
pytest tests/test_api/test_endpoints.py     # Single test file
pytest --cov=app tests/             # With coverage

black app/ tests/                   # Format
ruff check app/ tests/              # Lint
mypy app/ --ignore-missing-imports  # Type check
```

### Frontend (Next.js + TypeScript)

```bash
cd frontend
npm run dev       # Dev server on :3000
npm run build     # Production build
npm start         # Serve production build
npm run lint      # ESLint
```

### Infrastructure

```bash
# MongoDB via Docker
docker run -d --name seagull-mongo -p 27017:27017 mongo:7
```

API docs available at `http://localhost:8000/docs` when backend is running.

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Notes |
|----------|----------|-------|
| `OPENAI_API_KEY` | Yes | Validated at startup; raises `RuntimeError` if missing |
| `GOOGLE_CLIENT_ID` | Yes | OAuth |
| `GOOGLE_CLIENT_SECRET` | Yes | OAuth |
| `JWT_SECRET` | Yes | Token signing |
| `MONGODB_URI` | Yes | e.g. `mongodb://localhost:27017/Seagull` |
| `MONGO_DB` | Yes | e.g. `Seagull` |
| `FRONTEND_URL` | No | CORS + OAuth redirect (default: `http://localhost:3000`) |
| `RESEND_API_KEY` | No | Email invitations |

### Frontend (`frontend/.env.local`)

| Variable | Required |
|----------|----------|
| `NEXT_PUBLIC_API_URL` | Yes (e.g. `http://localhost:8000`) |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Yes |

## Architecture

### Backend (`backend/app/`)

Layered FastAPI structure:

- **`api/v1/`** — Route handlers (auth, papers, chat, verify, graph, workspace, conversations, cross_eval, doi, ws, files)
- **`core/`** — Foundational primitives: `rag.py`, `vector_db.py` (FAISS), `embeddings.py` (sentence-transformers), `llm.py` (OpenAI), `chunking.py`, `ws_manager.py`
- **`services/`** — Business logic per domain; called by API handlers
- **`verification/`** — Standalone claim verification engine (see below)
- **`tools/`** — LLM-powered extraction tools (graph builder, cross evaluator, method extractor, blueprint generator)
- **`models/`** — Pydantic schemas for requests/responses and MongoDB documents
- **`db/`** — MongoDB client helpers and initialization
- **`utils/`** — PDF parsing (PyPDF2), DOI fetching (Crossref), text processing (NLTK/SpaCy)

All settings are Pydantic-based in `config.py`, loaded from `.env`.

### Frontend (`frontend/`)

Next.js App Router with route groups:

- **`app/(dashboard)/`** — Authenticated pages: `chat/`, `claim-verify/`, `cross-eval/`, `graph/`, `pdf/`
- **`components/`** — Organized by feature: `auth/`, `layout/`, `chat/`, `pdf/`, `tools/`, `ui/` (Radix UI primitives)
- **`lib/api/`** — Axios clients per feature, all sharing a base instance with JWT auth header (`client.ts`)
- **`lib/ws/`** — WebSocket context provider + hooks
- **`lib/store/`** — Zustand store for active workspace and user state
- **`types/api.ts`** — Shared TypeScript interfaces for all API response shapes

### Key Data Flows

**PDF Ingestion**: Upload → parse (PyPDF2) → chunk (1000 chars, 200 overlap) → embed (all-MiniLM-L6-v2, 384-dim) → FAISS upsert → metadata enrichment via LLM (study type, citation count, domain) → intelligence extraction (methods, keywords, claims) → graph edge computation

**RAG Chat**: Query → embed → FAISS search (top_k=5) → build prompt with retrieved chunks → GPT-4o-mini → WebSocket broadcast to workspace → persist to MongoDB

**Claim Verification** (`verification/`):
1. `EvidenceRetriever` — FAISS search for relevant chunks
2. `EvidenceScorer` — Weighted formula: semantic (0.30) + study_type (0.25) + citation (0.20) + recency (0.15) + source (0.10)
3. `ClaimClassifier` — LLM classifies each chunk as `SUPPORT` / `CONTRADICT` / `NEUTRAL`
4. `ConfidenceAggregator` — `confidence = (support - contradict) / (support + contradict + ε)`
5. Guardrails: minimum 3 evidence chunks; contradiction override logic
6. Output: confidence label (Strong/Moderate/Weak/Inconclusive/Contradicted/Insufficient Evidence)

**Intelligence Graph**: Nodes = papers, concepts, methods, datasets. Edges = similarity (cosine ≥ 0.70), citation (DOI-matched), keyword overlap (≥3 shared keywords), contradiction (from cross-paper claim verification). Research gaps = concept nodes with only 1 connected paper. Visualized with `react-force-graph-2d`.

**Real-time Collaboration**: `ws_manager.py` maintains per-workspace WebSocket pools. Events: `new_message`, `typing_indicator`, `claim_verification_update`, `graph_update`. All workspace members receive live broadcasts.

### MongoDB Collections

`users`, `papers`, `chunks`, `workspaces`, `conversations`, `messages`, `verifications`

FAISS index stored at `./vector_db/faiss.index` (384-dim, IndexFlatL2). Use `backend/inspect_vector_db.py` to inspect it.
