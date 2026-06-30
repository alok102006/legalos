# MASTER PROMPT — LegalOS Production Build (Part 1 of 2: Core + Milestone 1)

You are building **LegalOS** — a production-grade AI Legal & Compliance Operating System for Indian SMEs. This is **not** a hackathon demo. Code must be modular, testable, properly layered, and structured so that new workspaces, models, or providers can be added without touching unrelated code. Prioritize correctness, separation of concerns, and maintainability over speed of delivery, while still shipping a fully working end-to-end system.

**This is Part 1 of a two-part build.** Part 1 covers the centralized AI/RAG core, the database, and Milestone 1 (Contract Intelligence) only. Stop after Milestone 1 is fully working — Vendor Intelligence and Legal Notice Center are out of scope for this prompt and will be delivered in Part 2. Do not scaffold their logic beyond empty placeholder folders if you want to leave room for them; do not build their routers, services, or UI yet.

Work milestone by milestone. After each milestone, run it and confirm it works before moving to the next. Do not skip the centralized AI core (Milestone 0) — Milestone 1 depends on it entirely.

---

## 1. Hard Constraints (do not violate)

1. **LLM abstraction layer is mandatory and centralized.** No feature module may ever call an LLM SDK directly. All AI access goes through a single core package, not per-workspace code.
2. **No real government/legal API integrations.** Mocked integrations (relevant in Part 2) must be clearly commented `# MOCKED — replace with real API integration` and isolated behind an interface.
3. **Database: PostgreSQL only.** No SQLite. All schemas must be normalized, versioned via migrations, and workspace tables must be logically namespaced (see schema section).
4. **Vector store: Qdrant only.** No Chroma, no in-memory cosine similarity, no Pinecone. Qdrant must be the single, centralized vector store, accessed by all workspaces through one retrieval service.
5. **Embeddings: `sentence-transformers/all-MiniLM-L6-v2` only.** No provider abstraction, no Gemini embeddings, no swappable embedding backends. This is a fixed, local, offline embedding model.
   - The model must be **loaded exactly once per process** (singleton, loaded at app startup or lazily on first use and cached in memory for the lifetime of the process) — never re-instantiated per request.
   - The model weights must be **cached to local disk** (via the standard `sentence-transformers`/HuggingFace cache directory, pinned to a project-local path e.g. `./model_cache` via `HF_HOME` / `SENTENCE_TRANSFORMERS_HOME` env vars) so it is downloaded from HuggingFace **once**, not on every container start or every request. The Docker setup must persist this cache directory as a volume so rebuilds/restarts reuse it instead of re-downloading.
   - Vector dimension is fixed at 384 (the known output dimension of `all-MiniLM-L6-v2`) — hardcode this explicitly in the Qdrant collection config, do not attempt to "detect" it at runtime.
6. **One centralized AI/RAG core**, shared by every workspace. Workspaces never instantiate their own embedding client, LLM client, chunker, or Qdrant client. They only call the core's public service interfaces.
7. **Strict backend/frontend separation.** Backend and frontend are independent deployable services with their own dependency files, own configs, and communicate only over a versioned REST API (`/api/v1/...`).
8. **Each workspace lives in its own isolated folder**, both backend and frontend, with no cross-workspace imports. Shared logic goes into `core/` or `shared/`, never duplicated per workspace.
9. **Frontend must be production-quality**: responsive, adaptive (mobile/tablet/desktop), accessible (WCAG AA basics — semantic HTML, keyboard nav, color contrast), with consistent design tokens, loading/error/empty states on every screen, and real auth-ready structure (even if auth is stubbed initially).
10. **Config-driven, not hardcoded.** All provider choices, model names, DB URLs, and API keys come from environment variables, validated at startup with a typed settings object (e.g. Pydantic `BaseSettings`).

---

## 2. Architecture Overview

```
                          ┌─────────────────────────┐
                          │        Frontend          │
                          │  (React + Vite + TS)     │
                          │  workspace-isolated UI   │
                          └────────────┬─────────────┘
                                       │ REST /api/v1
                          ┌────────────▼─────────────┐
                          │      API Gateway Layer     │
                          │   (FastAPI routers per     │
                          │    workspace, versioned)   │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │  Workspace: Contract Intel │
                          │  (own module — Part 1)     │
                          └────────────┬─────────────┘
                                       │ calls only
                          ┌────────────▼─────────────┐
                          │   Centralized AI/RAG Core   │
                          └─────────────┬─────────────┘
                                        │
                ┌───────────────────────┼───────────────────────┐
                │                       │                       │
        ┌───────▼─────┐       ┌─────────▼─────────┐     ┌───────▼─────┐
        │ llm_client   │       │ embedder            │     │ qdrant_store │
        │ (provider-   │       │ all-MiniLM-L6-v2     │     │ (single      │
        │  agnostic)   │       │ loaded once, cached   │     │  collection  │
        │              │       │ to local disk          │     │  manager)    │
        └───────┬─────┘       └──────────────────────┘     └──────────────┘
                │
        ┌───────▼─────────────┐
        │ Gemini 3.5 Flash      │
        │ (swappable: local LLM │
        │ via Ollama/vLLM later)│
        └───────────────────────┘
                                        │
                               ┌────────▼────────┐
                               │   PostgreSQL      │
                               │ (per-workspace     │
                               │  schemas/tables)   │
                               └────────────────────┘
```

Key rule: **arrows only point from a workspace into the core. The core never imports from a workspace.** Vendor Intelligence and Legal Notice Center will plug into the same core in Part 2 — build the core generically, not contract-specific, even though only Contract Intelligence consumes it right now.

---

## 3. Folder Structure (authoritative for this build — Part 2 will add to it, do not deviate)

```
legalos/
│
├── backend/
│   ├── pyproject.toml                  # or requirements.txt + setup.cfg
│   ├── alembic.ini
│   ├── .env.example
│   ├── app/
│   │   ├── main.py                     # FastAPI app factory, mounts all workspace routers
│   │   ├── config.py                   # Pydantic BaseSettings — single source of env config
│   │   ├── dependencies.py             # shared FastAPI dependencies (DB session, auth, etc.)
│   │   │
│   │   ├── core/                       # ★ CENTRALIZED AI / RAG CORE — shared by ALL workspaces
│   │   │   ├── __init__.py
│   │   │   ├── llm/
│   │   │   │   ├── llm_client.py       # generate(prompt, system="", json_mode=False) -> str
│   │   │   │   ├── providers/
│   │   │   │   │   ├── gemini_provider.py
│   │   │   │   │   └── local_provider.py   # stub for future Ollama/vLLM
│   │   │   │   └── prompts/            # ALL prompts live here, namespaced per workspace
│   │   │   │       └── contract_intel_prompts.py
│   │   │   ├── embeddings/
│   │   │   │   └── embedder.py         # singleton-loaded all-MiniLM-L6-v2, embed(texts) -> vectors
│   │   │   ├── vectorstore/
│   │   │   │   ├── qdrant_client.py    # single Qdrant connection/session manager
│   │   │   │   ├── collections.py      # collection schema definitions per workspace
│   │   │   │   └── retrieval_service.py# upsert(), search(), delete() — the only public API
│   │   │   ├── rag/
│   │   │   │   ├── chunker.py          # shared text chunking strategies
│   │   │   │   ├── rag_pipeline.py     # orchestrates: chunk -> embed -> upsert / retrieve -> generate
│   │   │   │   └── document_parser.py  # PDF/DOCX/text parsing shared across workspaces
│   │   │   └── schemas/
│   │   │       └── ai_io_schemas.py    # shared Pydantic models for AI request/response shapes
│   │   │
│   │   ├── shared/                     # non-AI shared utilities
│   │   │   ├── db/
│   │   │   │   ├── base.py             # SQLAlchemy declarative base
│   │   │   │   ├── session.py          # async session factory
│   │   │   │   └── mixins.py           # created_at/updated_at/UUID PK mixins
│   │   │   ├── storage/
│   │   │   │   └── file_storage.py     # local/S3-ready abstraction for uploaded files
│   │   │   ├── auth/
│   │   │   │   └── auth_service.py     # stubbed role-based auth (Owner/CA/Reviewer)
│   │   │   └── exceptions.py
│   │   │
│   │   ├── workspaces/
│   │   │   ├── contract_intelligence/  # ★ BUILD THIS IN PART 1
│   │   │   │   ├── router.py           # /api/v1/contracts/*
│   │   │   │   ├── service.py          # business logic, calls core.rag / core.llm only
│   │   │   │   ├── models.py           # SQLAlchemy models (contracts, clauses, risk_flags)
│   │   │   │   ├── schemas.py          # Pydantic request/response models
│   │   │   │   └── repository.py       # DB access layer
│   │   │   │
│   │   │   ├── vendor_intelligence/    # PART 2 — leave empty/placeholder only
│   │   │   ├── legal_notice_center/    # PART 2 — leave empty/placeholder only
│   │   │   ├── compliance_center/      # Phase 2 — out of scope entirely
│   │   │   └── knowledge_hub/          # Phase 2 — out of scope entirely
│   │   │
│   │   └── migrations/                 # Alembic migration scripts
│   │
│   └── tests/
│       ├── core/
│       └── workspaces/
│           └── contract_intelligence/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── .env.example
│   └── src/
│       ├── main.tsx
│       ├── App.tsx                     # router shell, layout, theme provider
│       ├── design-system/              # ★ shared design tokens & primitives, used by ALL workspaces
│       │   ├── tokens.ts               # colors, spacing, typography scale
│       │   ├── components/             # Button, Card, Badge, Modal, Toast, RiskBadge, etc.
│       │   └── layout/
│       │       ├── AppShell.tsx        # responsive shell: sidebar (desktop) / bottom nav (mobile)
│       │       └── WorkspaceNav.tsx
│       ├── api/
│       │   ├── client.ts               # single axios/fetch instance, interceptors, base URL
│       │   └── types.ts                # shared API response types
│       ├── workspaces/
│       │   └── contract-intelligence/  # ★ BUILD THIS IN PART 1
│       │       ├── pages/
│       │       ├── components/
│       │       ├── hooks/
│       │       └── api.ts              # calls only /api/v1/contracts/*
│       └── lib/
│           ├── auth/                   # fake-login role switcher (Owner/CA/Reviewer)
│           └── hooks/                  # generic hooks: useDebounce, useResponsive, etc.
│
├── docker-compose.yml                  # postgres + qdrant + backend + frontend, local dev only
├── .env.example                        # root-level shared vars (ports, etc.)
└── README.md
```

**Rule for the agent:** if a piece of logic might be needed by more than one workspace, it belongs in `core/` or `shared/` even if only Contract Intelligence uses it today — never write it in a way that assumes contracts are the only document type. `vendor_intelligence/` and `legal_notice_center/` folders should exist as empty placeholders with a `.gitkeep` only; do not implement anything inside them in this part of the build.

---

## 4. Centralized AI / RAG Core — Required Interfaces

All workspaces consume the core through these contracts only. Implement the core first, write a smoke test for each, and only then start workspace code.

### `core/llm/llm_client.py`
```python
def generate(prompt: str, system: str = "", json_mode: bool = False, workspace: str = "") -> str:
    """
    Single entrypoint for all LLM calls in the system.
    Reads LLM_PROVIDER from settings ("gemini" | "local").
    Routes to the matching provider in core/llm/providers/.
    `workspace` is passed only for logging/telemetry, never for branching logic.
    """
```
- `LLM_PROVIDER=gemini` → uses `gemini-3.5-flash` (or latest fast Gemini model) via the official SDK.
- Adding `local` (OpenAI-compatible endpoint, e.g. Ollama at `http://localhost:11434/v1`) must require editing **only** `providers/local_provider.py` and the provider switch in `llm_client.py`.
- All retries, timeouts, and error normalization happen here — not in workspace code.

### `core/embeddings/embedder.py`
```python
class Embedder:
    """
    Singleton wrapper around sentence-transformers/all-MiniLM-L6-v2.
    - Model is loaded exactly once: either at app startup (preferred, via FastAPI lifespan)
      or lazily on first call, then cached as a module/class-level instance for the life
      of the process. Never call SentenceTransformer(...) inside a request handler.
    - Model cache directory is pinned via env (HF_HOME / SENTENCE_TRANSFORMERS_HOME) to a
      project-local, volume-mounted path so weights are downloaded from HuggingFace once
      and reused across container restarts/rebuilds.
    - Exposes a module-level singleton accessor, e.g. get_embedder() -> Embedder, so the
      rest of the codebase never re-instantiates the model.
    """

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Returns 384-dim vectors using all-MiniLM-L6-v2. Batches internally for efficiency."""
```
- No provider abstraction layer for embeddings — this is intentionally a fixed, local, single-model utility, unlike the LLM client which stays swappable.
- Log a clear one-time startup message confirming whether the model was loaded from local cache or downloaded fresh, so cache-hit vs cache-miss is visible during development.

### `core/vectorstore/retrieval_service.py`
```python
def upsert_chunks(collection: str, items: list[ChunkRecord]) -> None: ...
def search(collection: str, query: str, top_k: int = 5, filters: dict | None = None) -> list[RetrievedChunk]: ...
def delete_by_document(collection: str, document_id: str) -> None: ...
```
- Qdrant is the **only** vector backend. One Qdrant client instance, reused across the app (connection pooling, not re-instantiated per request).
- Each workspace gets its own **named Qdrant collection** (only `contract_clauses` in Part 1) but all collections are created/managed centrally via `core/vectorstore/collections.py` — workspaces declare their schema there, they don't create collections themselves.
- Collection vector size is fixed at **384** (matching `all-MiniLM-L6-v2`), cosine distance.

### `core/rag/rag_pipeline.py`
```python
def ingest_document(file_bytes: bytes, filename: str, workspace: str, metadata: dict) -> str:
    """parse -> chunk -> embed -> upsert into the correct Qdrant collection. Returns document_id."""

def retrieve_and_generate(query: str, workspace: str, system_prompt: str, top_k: int = 5, json_mode: bool = False) -> str:
    """retrieve relevant chunks -> build context -> call llm_client.generate(). The standard RAG call every workspace should use."""
```
- `core/rag/document_parser.py` centralizes PyMuPDF (PDF) and python-docx (Word) parsing — implement once so it's reusable for contracts now and notices later (Part 2).
- `core/rag/chunker.py` centralizes chunking strategy(ies), exposed as named strategies (`chunk_by_clause` for Part 1; `chunk_by_paragraph` will be added in Part 2) so workspaces select a strategy, not reimplement one.

---

## 5. Database — PostgreSQL Schema Design (Part 1 scope)

Use SQLAlchemy (async) + Alembic migrations. Use **one PostgreSQL database**, with a **dedicated schema (namespace) per workspace**. Only `core` and `contract_intelligence` schemas are needed for Part 1; leave the migration structure ready to add `vendor_intelligence` and `legal_notice_center` schemas in Part 2 without restructuring anything.

```sql
-- shared/core schema
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE core.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('business_owner', 'ca', 'legal_reviewer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE core.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace TEXT NOT NULL,              -- 'contract_intelligence' for Part 1
    original_filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    uploaded_by UUID REFERENCES core.users(id),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- contract_intelligence schema
CREATE SCHEMA IF NOT EXISTS contract_intelligence;

CREATE TABLE contract_intelligence.contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES core.documents(id) ON DELETE CASCADE,
    title TEXT,
    counterparty_name TEXT,
    status TEXT NOT NULL DEFAULT 'processing' CHECK (status IN ('processing', 'analyzed', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE contract_intelligence.clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contract_intelligence.contracts(id) ON DELETE CASCADE,
    clause_index INT NOT NULL,
    raw_text TEXT NOT NULL,
    summary TEXT,
    risk_type TEXT CHECK (risk_type IN ('penalty', 'lock_in', 'indemnity', 'termination', 'none')),
    risk_score INT CHECK (risk_score BETWEEN 0 AND 100),
    qdrant_point_id UUID,                 -- link to vector store record
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE contract_intelligence.negotiation_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clause_id UUID NOT NULL REFERENCES contract_intelligence.clauses(id) ON DELETE CASCADE,
    suggestion_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Migration rules for the agent:
- One Alembic migration per logical change, never hand-edit the DB.
- Every workspace's models live in its own `models.py`, but Alembic's `env.py` imports all of them centrally so a single `alembic upgrade head` migrates everything (including future Part 2 schemas, once added).
- Use `UUID` primary keys (`gen_random_uuid()` via `pgcrypto` extension) everywhere — no autoincrement integers.

---

## 6. Qdrant Collection Design (Part 1 scope)

One Qdrant instance. Only one collection is created in Part 1, but `collections.py` should be structured as a registry so Part 2 can add entries without touching Part 1's code:

| Collection | Used by | Payload fields |
|---|---|---|
| `contract_clauses` | Contract Intelligence | `document_id`, `contract_id`, `clause_index`, `risk_type`, `risk_score` |

Vector size: **384** (fixed, `all-MiniLM-L6-v2` output dimension). Distance metric: cosine.

---

## 7. Milestone 0 — Centralized Core (build first, nothing else proceeds without it)

- `core/llm`, `core/embeddings`, `core/vectorstore`, `core/rag` fully implemented per section 4.
- `Embedder` singleton confirmed to load the model exactly once per process — add a unit test or manual check that calling `get_embedder()` twice returns the same in-memory instance, and that a second app start reuses the cached weights on disk (no re-download).
- Smoke test: one script that proves an end-to-end `ingest_document` → `retrieve_and_generate` round trip works against a real PDF, using only local embeddings + Gemini for generation.
- Postgres + Qdrant running via `docker-compose.yml` (with the embedding model cache mounted as a persistent volume), Alembic baseline migration applied.

## 8. Milestone 1 — Contract Intelligence (the core pitch — build this, then stop)

- Upload PDF/DOCX → `core.rag.rag_pipeline.ingest_document()` → clause-level chunking → for each chunk call `llm_client.generate(json_mode=True)` for `{summary, risk_type, risk_score}`.
- Persist clauses + risk metadata in `contract_intelligence.clauses`; also upsert into Qdrant `contract_clauses` collection (using the local `all-MiniLM-L6-v2` embeddings) for later semantic search/reuse.
- UI: color-coded clause list (green/yellow/red by `risk_score`), filterable by risk type.
- "Generate Negotiation Suggestions" — sends flagged clauses back through `core.rag.retrieve_and_generate` for plain-English counter-proposals, persisted to `negotiation_suggestions`.

---

## 9. Frontend Requirements (applies to Milestone 1 UI)

1. **Design system first.** Build `design-system/tokens.ts` (colors, spacing, typography, radii) and a small set of primitives (`Button`, `Card`, `Badge`, `RiskBadge`, `Modal`, `Toast`, `Skeleton`) before the Contract Intelligence UI. These primitives must be generic enough for Part 2's workspaces to reuse without modification.
2. **Responsive & adaptive:** mobile-first Tailwind breakpoints; `AppShell` renders a sidebar nav on desktop/tablet and a bottom tab bar on mobile; clause lists/tables collapse to stacked cards below `md`.
3. **States on every screen:** loading (skeletons, not spinners-only), empty state, error state with retry, and success state. No screen should ever render blank while data is in flight.
4. **Accessibility baseline:** semantic landmarks (`nav`, `main`, `header`), labeled form inputs, focus-visible states, sufficient color contrast for risk badges (don't rely on color alone — pair with icon/text).
5. **Fake-login role switcher** (Business Owner / CA / Legal Reviewer) lives in `lib/auth/`, structured so swapping in real auth (JWT/OAuth) later only touches that folder, not workspace code.
6. **API layer:** single `api/client.ts` instance (base URL from env, interceptors for error normalization); Contract Intelligence's `api.ts` only calls `/api/v1/contracts/*`.

---

## 10. Build Instructions for the Agent (sequenced)

1. Scaffold the full folder structure from section 3 exactly (empty files/folders are fine initially; `vendor_intelligence/`, `legal_notice_center/`, `compliance_center/`, `knowledge_hub/` stay as placeholders only).
2. Stand up `docker-compose.yml` with `postgres`, `qdrant`, `backend`, `frontend` services, plus a named volume for the sentence-transformers model cache. Confirm all services boot and health-check.
3. Implement `app/config.py` (typed settings, validated env vars) before anything else reads an env var.
4. Build **Milestone 0** (centralized AI/RAG core) completely, with a smoke-test script confirming both the LLM round trip and the embedding-model singleton/caching behavior, before writing any workspace code.
5. Apply the baseline Alembic migration (section 5 schemas) and confirm `psql` shows `core` and `contract_intelligence` schemas/tables.
6. Build **Milestone 1** end-to-end (upload → parse → chunk → LLM analysis → persisted → rendered UI). Run and visually confirm.
7. Add `.env.example` at root, `backend/`, and `frontend/` covering: `LLM_PROVIDER=gemini`, `GEMINI_API_KEY=`, `DATABASE_URL=postgresql+asyncpg://...`, `QDRANT_URL=`, `QDRANT_API_KEY=`, `HF_HOME=/app/model_cache`, `SENTENCE_TRANSFORMERS_HOME=/app/model_cache`.
8. Write at minimum one unit test per core module (`llm_client`, `embedder`, `retrieval_service`, `rag_pipeline`) and one integration test for Contract Intelligence's primary flow.
9. **Stop here.** Do not begin Vendor Intelligence or Legal Notice Center — those are covered in Part 2 of this prompt.

---

## 11. Definition of Done (Part 1)

Part 1 is complete only when:
- It runs end-to-end via `docker-compose up` with no manual steps beyond seeding `.env`.
- All AI calls are traceable to `core/llm/llm_client.py` (grep the workspace folder for any direct provider SDK import — there should be none).
- All vector operations are traceable to `core/vectorstore/retrieval_service.py` (no workspace imports `qdrant_client` directly).
- The embedding model is loaded once per process and its weights are cached to a persistent local volume — restarting the backend container does **not** trigger a re-download from HuggingFace (verify by checking logs on a second start).
- Data persists correctly in `core` and `contract_intelligence` PostgreSQL schemas and survives a container restart.
- The Contract Intelligence frontend renders loading/empty/error/success states and is usable on a 375px-wide viewport.
