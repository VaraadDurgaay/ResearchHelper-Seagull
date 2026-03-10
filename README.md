# Seagull — Research Intelligence Platform

Seagull is a collaborative research workspace built around **claim-level verification** and a **research intelligence graph**. Unlike tools that summarize papers, Seagull lets you audit factual claims against your uploaded papers with scored evidence, confidence levels, and citation traceability.

---

## Features

- **PDF Workspaces** — Upload PDFs or import by DOI into shared workspaces. Collaborate with teammates via invite links.
- **RAG Chat** — Ask questions across all papers in your workspace. Answers include citations scoped to your papers.
- **Claim Verification** — Submit an atomic claim (e.g. *"Coffee reduces anxiety in adults"*) and get structured output: support / contradict / neutral counts, a confidence score, evidence strength, and per-chunk scored evidence. No free-form prose.
- **Research Intelligence Graph** — Visualise relationships between papers, methods, datasets, and concepts. Edges represent similarity, citation, keyword overlap, and contradiction. Research gaps are highlighted automatically.
- **Cross-Eval** — Send the same question to the model for each paper independently and compare answers side by side.
- **Real-time Collaboration** — WebSocket broadcasts keep all workspace members in sync on chat, claim verifications, and graph updates.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Database | MongoDB |
| Vector store | FAISS (CPU) |
| Embeddings | `sentence-transformers` (local) or OpenAI (`text-embedding-3-small`) |
| LLM | OpenAI (`gpt-4o-mini`) |
| Auth | Google OAuth + JWT |
| Frontend | Next.js 16, React 19, TypeScript 5 |
| UI | Tailwind CSS 4, Radix UI, Lucide |
| Graph | `react-force-graph-2d` |

---

## Project Structure

```
Seagull/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers (papers, chat, verify, graph, …)
│   │   ├── core/            # RAG, embeddings, FAISS, WebSocket manager
│   │   ├── services/        # Business logic layer
│   │   ├── verification/    # Claim verification engine
│   │   ├── db/              # MongoDB helpers
│   │   └── models/          # Pydantic schemas
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   └── (dashboard)/     # chat / claim-verify / graph / cross-eval pages
│   ├── components/
│   ├── lib/api/             # Axios API client per feature
│   └── package.json
└── docker-compose.yml
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (for MongoDB)
- An OpenAI API key
- A Google OAuth client ID and secret

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/VaraadDurgaay/ResearchHelper-Seagull.git
cd ResearchHelper-Seagull
```

### 2. Start MongoDB

```bash
docker run -d --name seagull-mongo -p 27017:27017 mongo:7
```

### 3. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OPENAI_API_KEY=sk-...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
JWT_SECRET=your-random-secret
MONGODB_URI=mongodb://localhost:27017/Seagull
MONGO_DB=Seagull
FRONTEND_URL=http://localhost:3000
```

Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=...
```

Start the dev server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## API Overview

All routes live under `/api/v1/`. Protected routes require a `Bearer` token in the `Authorization` header and the active workspace in the `X-Workspace-Id` header.

| Method | Route | Description |
|---|---|---|
| `POST` | `/auth/google` | Exchange Google ID token for JWT |
| `GET` | `/auth/me` | Current user info |
| `POST` | `/papers/` | Upload a PDF |
| `POST` | `/doi/import` | Import paper by DOI |
| `POST` | `/chat/` | RAG chat over workspace papers |
| `POST` | `/verify/claim` | Verify a claim against workspace papers |
| `GET` | `/verify/recent` | Recent claim verification runs |
| `GET` | `/graph/workspace/intelligence` | Intelligence graph (nodes + edges) |
| `POST` | `/cross-eval/` | Cross-paper evaluation |
| `GET` | `/workspaces/` | List workspaces |
| `POST` | `/workspaces/{id}/invite` | Invite a collaborator |

Interactive docs available at [http://localhost:8000/docs](http://localhost:8000/docs) when the backend is running.

---

## Claim Verification

The verification engine scores each evidence chunk against your claim using a weighted formula:

```
evidence_score = 0.30 × semantic
               + 0.25 × study_type
               + 0.20 × citation_count
               + 0.15 × recency
               + 0.10 × source_credibility
```

Study type hierarchy: `meta-analysis > RCT > systematic review > cohort > observational`

Guardrails enforce a minimum of 3 evidence chunks and override the confidence label to `Contradicted` when contradiction weight exceeds support weight.

---

## Intelligence Graph

After upload, a background job extracts per-paper intelligence (methods, datasets, keywords, claims, domain) using the LLM. The graph then builds:

- **Similarity edges** — cosine similarity ≥ 0.70 between paper embeddings
- **Citation edges** — DOI-matched references from paper metadata
- **Keyword overlap edges** — ≥ 3 meaningful shared keywords (academic stopwords excluded)
- **Contradiction edges** — derived from claim verification runs where the same claim has both SUPPORT and CONTRADICT evidence across different papers

Concept nodes with only one connected paper are marked as **research gaps**.

---

## License

MIT
