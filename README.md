# ResearchPilot

An AI-powered research workspace for uploading academic papers, chatting with them via retrieval-augmented generation (RAG), classifying their figures with computer vision, comparing papers structurally, and tracking research experiments.

This is a full-stack portfolio project demonstrating production-oriented application architecture across frontend, backend, database design, LLM integration, RAG, and computer vision.

> **Note on AI providers:** By default the app runs with `LLM_PROVIDER=mock` and `VISION_PROVIDER=mock` — deterministic, dependency-light, offline implementations that perform *real* extractive text analysis and *real* pixel-level image analysis (no canned strings, no network calls), so the whole application is runnable and testable without API keys. Set `LLM_PROVIDER=openai` (with `OPENAI_API_KEY`) and `VISION_PROVIDER=clip` (with `requirements-vision.txt` installed) for production-quality generative answers and neural figure classification. Every part of the app that talks to AI goes through the same abstraction either way — see [LLM Abstraction](#llm-abstraction).

---

## 1. Features

- **Authentication** — email/password registration and login with JWT bearer tokens, bcrypt password hashing.
- **Paper upload & processing** — PDF upload with type/size validation, background ingestion pipeline (text/metadata extraction, section splitting, chunking, embeddings, figure extraction, vision classification, summarization), and pollable processing status (`uploaded → processing → ready/failed`).
- **RAG chat** — ask natural-language questions about a specific paper; answers are grounded in the top-K retrieved chunks (pgvector cosine similarity) and cite the source section.
- **Figure analysis** — figures are extracted from the PDF, classified into one of 7 categories, and described automatically.
- **Paper comparison** — structured, schema-constrained comparison of 2+ papers (research problem, methodology, datasets, models, results, strengths, limitations, key differences).
- **Experiment tracking** — log model/dataset/hyperparameters, record metrics over time, and visualize them as charts.
- **Dashboard & search** — workspace-wide stats and full-text search across papers, chunks, and experiments.
- **Observability** — every AI call (LLM or vision) is recorded as an `ai_inferences` row with latency, token usage, and success/failure.
- **Strict per-user authorization** — every resource lookup is scoped to `owner_id`/`user_id`; cross-user access returns `404`, never `403` (avoids leaking existence).

## 2. Screenshots

_This is a freshly scaffolded project — run it locally (see [Local Setup](#8-local-setup)) to see the landing page, dashboard, paper chat, and figure analysis views in your browser._

## 3. Architecture

```mermaid
flowchart TD
    subgraph Client
        FE[Next.js Frontend]
    end

    subgraph API["FastAPI Backend"]
        AUTH[Auth Service]
        PAPER[Paper Service]
        DOC[Document Processor]
        RAG[RAG Service]
        LLM[LLM Abstraction]
        VIS[Vision Abstraction]
        CONV[Conversation Service]
        EXP[Experiment Service]
        ANALYTICS[Analytics Service]
    end

    DB[(PostgreSQL + pgvector)]
    STORAGE[(File Storage: PDFs + Figures)]
    OPENAI[[OpenAI API]]
    CLIP[[CLIP Vision Model]]

    FE -->|REST + JWT| API
    AUTH --> DB
    PAPER --> DOC
    DOC --> STORAGE
    PAPER --> LLM
    PAPER --> VIS
    RAG --> LLM
    RAG --> DB
    CONV --> DB
    EXP --> DB
    ANALYTICS --> DB
    LLM -.optional.-> OPENAI
    VIS -.optional.-> CLIP
    PAPER --> DB
```

### Background processing

Paper ingestion is expensive (PDF parsing, embedding generation, vision inference), so it never runs on the request thread. Upload returns immediately with `status=uploaded`, and a FastAPI `BackgroundTask` runs the full pipeline out-of-band:

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant BG as Background Task
    participant DB as PostgreSQL

    U->>API: POST /api/papers (PDF)
    API->>DB: insert Paper(status=uploaded)
    API-->>U: 201 Created (paper record)
    API->>BG: schedule process_paper_job(paper_id)
    BG->>DB: status=processing
    BG->>BG: extract text/sections/figures (PyMuPDF)
    BG->>BG: chunk + embed sections
    BG->>DB: insert chunks + embeddings (pgvector)
    BG->>BG: classify + describe figures (vision provider)
    BG->>DB: insert figures
    BG->>BG: generate AI summary (LLM provider)
    BG->>DB: status=ready (or failed + error)
    U->>API: GET /api/papers/{id}/status (poll)
    API-->>U: current status
```

For a production deployment beyond this portfolio scope, swap `BackgroundTasks` for a real queue (Celery/RQ + Redis) behind the same `process_paper_job` entry point — see [Future Improvements](#14-future-improvements).

## 4. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, React, Tailwind CSS, TanStack Query, Recharts |
| Backend | Python, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL 16 + pgvector |
| Document processing | PyMuPDF (text/metadata/figure extraction) |
| Vision | Heuristic pixel-analysis provider (default) or CLIP zero-shot classification (optional) |
| LLM | Pluggable `LLMProvider` — OpenAI Chat Completions + Embeddings, or an offline mock |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Infra | Docker, docker-compose |
| Testing | pytest (backend) |

## 5. Database Schema

```mermaid
erDiagram
    USERS ||--o{ PAPERS : owns
    USERS ||--o{ CONVERSATIONS : starts
    USERS ||--o{ EXPERIMENTS : owns
    PAPERS ||--o{ PAPER_SECTIONS : has
    PAPERS ||--o{ PAPER_CHUNKS : has
    PAPERS ||--o{ FIGURES : has
    PAPERS ||--o{ CONVERSATIONS : discussed_in
    PAPER_SECTIONS ||--o{ PAPER_CHUNKS : split_into
    CONVERSATIONS ||--o{ MESSAGES : contains
    EXPERIMENTS ||--o{ EXPERIMENT_METRICS : logs

    USERS {
        uuid id PK
        string email
        string hashed_password
    }
    PAPERS {
        uuid id PK
        uuid owner_id FK
        string title
        string status
        text abstract
        text ai_summary
    }
    PAPER_SECTIONS {
        uuid id PK
        uuid paper_id FK
        string title
        text content
        int order_index
    }
    PAPER_CHUNKS {
        uuid id PK
        uuid paper_id FK
        uuid section_id FK
        text content
        vector embedding
    }
    FIGURES {
        uuid id PK
        uuid paper_id FK
        int page_number
        string classification
        float confidence
        text description
    }
    CONVERSATIONS {
        uuid id PK
        uuid paper_id FK
        uuid user_id FK
    }
    MESSAGES {
        uuid id PK
        uuid conversation_id FK
        string role
        text content
    }
    EXPERIMENTS {
        uuid id PK
        uuid owner_id FK
        string name
        string model
    }
    EXPERIMENT_METRICS {
        uuid id PK
        uuid experiment_id FK
        string name
        float value
    }
    ANALYSES {
        uuid id PK
        uuid paper_id FK
        string analysis_type
        text content
    }
    AI_INFERENCES {
        uuid id PK
        string operation
        string provider
        int latency_ms
        boolean success
    }
```

All primary keys are UUIDs. Foreign keys cascade on delete (deleting a paper removes its sections, chunks, figures, and conversations). See [`backend/alembic/versions/0001_initial_schema.py`](backend/alembic/versions/0001_initial_schema.py) for the full DDL, including the `ivfflat` cosine-distance index on `paper_chunks.embedding`.

## 6. RAG Pipeline

```
PDF → PyMuPDF text extraction → section splitting (heading regex) → cleaning
    → word-window chunking (800 words, 150 overlap) → embedding (LLM provider)
    → pgvector storage
    → [user question] → question embedding → cosine similarity search (top 5)
    → context assembly with section labels → LLM generation (grounded system prompt)
    → answer + citations back to the frontend
```

The RAG system prompt (`app/services/rag_service.py`) explicitly instructs the model to:
- answer only from the supplied context,
- say so when the context is insufficient rather than guessing,
- tag claims with their source section (e.g. `(Section: Methodology)`),
- prefix interpretation separately from paper claims.

Retrieval never sends the whole paper to the LLM — only the top-K most relevant chunks by cosine similarity.

## 7. Vision Pipeline

```
PDF → per-page image extraction (PyMuPDF) → filter decorative/tiny images
    → save to /storage/figures/{paper_id}/ → vision provider classification
    → one of: architecture_diagram, flowchart, graph_plot, table,
              microscopy_image, mathematical_figure, other
    → confidence score + natural-language description → stored on Figure row
```

Two interchangeable providers implement `VisionProvider`:
- **`heuristic-cv` (default, `VISION_PROVIDER=mock`)** — real image analysis (edge density, color variance, background fraction, aspect ratio computed with Pillow/NumPy) mapped to a figure class via explainable rules. No heavy ML dependency required.
- **CLIP (`VISION_PROVIDER=clip`)** — real zero-shot classification using `openai/clip-vit-base-patch32` via HuggingFace `transformers`. Install `backend/requirements-vision.txt` to enable.

## 8. LLM Abstraction

All AI text generation goes through `app/services/llm/base.py`:

```python
class LLMProvider(ABC):
    def generate(self, system_prompt, user_prompt, *, temperature=0.2) -> LLMResult: ...
    def generate_structured(self, system_prompt, user_prompt, schema, *, temperature=0.0) -> StructuredResult: ...
    def embed(self, texts: list[str]) -> EmbeddingResult: ...
```

- `OpenAIProvider` implements this against the real Chat Completions + Embeddings APIs (JSON-schema-constrained structured output for comparisons/metadata extraction).
- `MockLLMProvider` implements it with deterministic extractive summarization/QA and a hash-based bag-of-words embedding — no network calls, fully offline, used by default and in tests.

No route or service calls a vendor SDK directly — they all depend on `get_llm_provider()`, so adding a new model/vendor means implementing one class.

## 9. API Documentation

Interactive OpenAPI docs are served at `http://localhost:8000/docs` once the backend is running. Summary of the REST surface:

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Create an account, returns a JWT |
| POST | `/api/auth/login` | Log in, returns a JWT |
| GET | `/api/auth/me` | Current user |
| POST | `/api/papers` | Upload a PDF (multipart) |
| GET | `/api/papers` | List your papers (supports `q`, `status_filter`) |
| GET | `/api/papers/{id}` | Paper detail incl. sections |
| DELETE | `/api/papers/{id}` | Delete a paper |
| GET | `/api/papers/{id}/status` | Poll processing status |
| POST | `/api/papers/{id}/process` | Re-run the ingestion pipeline |
| POST | `/api/papers/{id}/chat` | Ask a grounded question (RAG) |
| GET | `/api/papers/{id}/conversations` | List conversations for a paper |
| GET | `/api/conversations/{id}` | Conversation detail with messages |
| POST | `/api/papers/{id}/summarize` | (Re)generate the AI summary |
| POST | `/api/papers/compare` | Structured comparison of 2+ papers |
| GET | `/api/papers/{id}/figures` | List extracted figures |
| POST | `/api/figures/{id}/analyze` | Re-run vision classification on one figure |
| POST/GET/PUT/DELETE | `/api/experiments[/{id}]` | Experiment CRUD |
| POST/GET | `/api/experiments/{id}/metrics` | Log/list metrics |
| GET | `/api/dashboard` | Workspace stats + recents |
| GET | `/api/search?q=` | Cross-entity search |

All errors are returned as `{"error": {"code": "...", "message": "..."}}` with an appropriate HTTP status. No stack traces are ever exposed to the client — unhandled exceptions are logged server-side and returned as a generic `INTERNAL_ERROR`.

## 10. Local Setup

### With Docker (recommended)

```bash
git clone <this-repo>
cd researchpilot
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Postgres: localhost:5432

The backend container runs `alembic upgrade head` automatically on startup.

### Without Docker

Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp ../.env.example ../.env   # edit DATABASE_URL to point at your local Postgres
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

You'll need a local PostgreSQL with the `pgvector` extension available (`CREATE EXTENSION vector;`) — the `pgvector/pgvector:pg16` Docker image already includes it.

## 11. Environment Variables

See [`.env.example`](.env.example) for the full list. Key ones:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string |
| `JWT_SECRET_KEY` | Signing key for access tokens — **change in production** |
| `LLM_PROVIDER` | `mock` (default, offline) or `openai` |
| `OPENAI_API_KEY` | Required when `LLM_PROVIDER=openai` |
| `VISION_PROVIDER` | `mock` (default, offline heuristic) or `clip` |
| `MAX_UPLOAD_MB` | PDF upload size limit |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed origins |
| `NEXT_PUBLIC_API_URL` | Backend URL the frontend calls |

Never commit `.env` — only `.env.example` is tracked.

## 12. Running Tests

Backend tests require a real PostgreSQL instance with `pgvector` (used for cosine-distance retrieval tests) — point `TEST_DATABASE_URL` at a scratch database:

```bash
cd backend
docker run -d --name rp-test-db -e POSTGRES_USER=researchpilot -e POSTGRES_PASSWORD=researchpilot \
  -e POSTGRES_DB=researchpilot_test -p 5433:5432 pgvector/pgvector:pg16
export TEST_DATABASE_URL=postgresql+psycopg://researchpilot:researchpilot@localhost:5433/researchpilot_test
pytest -v
```

Tests cover: registration/login, cross-user authorization on papers and experiments, the RAG retrieval+answer flow, structured paper comparison, chunking logic, and the heuristic vision classifier.

## 13. Deployment

- **Backend**: any container platform (Fly.io, Render, Railway, ECS). Point `DATABASE_URL` at a managed Postgres with the `vector` extension enabled (Neon, Supabase, and RDS all support it), run `alembic upgrade head` as a release step, and mount persistent storage for `STORAGE_DIR` (or swap `paper_service.py`/`main.py` to use S3-compatible object storage for `file_path`/`image_path`).
- **Frontend**: Vercel (native Next.js support) or any Node host — set `NEXT_PUBLIC_API_URL` to the deployed backend URL.
- **Secrets**: set `JWT_SECRET_KEY` and `OPENAI_API_KEY` via the platform's secret manager, never in source.
- **CORS**: set `BACKEND_CORS_ORIGINS` to the deployed frontend origin(s).

## 14. Future Improvements

- Replace `BackgroundTasks` with a durable queue (Celery/RQ + Redis) for retryable, horizontally-scalable ingestion.
- Streaming chat responses (SSE/WebSocket) instead of a single blocking `POST /chat`.
- Reference/citation extraction and a "cited by" graph across the user's library.
- Object storage (S3/GCS) for uploaded PDFs and extracted figures instead of local disk.
- Admin view over the `ai_inferences` table for cost/latency dashboards.
- Frontend component tests (Vitest + Testing Library) for the chat and upload flows.

## 15. Repository Layout

```
researchpilot/
  backend/
    app/
      api/routes/       # FastAPI routers (thin — delegate to services)
      services/         # Business logic: RAG, vision, document processing, LLM abstraction
      models/           # SQLAlchemy models
      schemas/          # Pydantic request/response models
      core/             # Security, dependencies, structured errors
    alembic/            # Migrations
    tests/              # pytest suite
  frontend/
    src/app/            # Next.js App Router pages
    src/components/     # Shared + paper-tab React components
    src/lib/            # API client, types, auth context
  docker-compose.yml
  .env.example
```
