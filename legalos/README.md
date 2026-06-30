# LegalOS — AI Legal & Compliance Operating System for Indian SMEs

LegalOS is a multi-workspace production-grade system designed for Indian SMEs to manage legal and compliance needs.

## LICENSE NOTE
> [!WARNING]
> This project uses **PyMuPDF** (via the `pymupdf` library) for PDF parsing, which is licensed under the **GNU AGPL (Affero General Public License)**. If this application is distributed or deployed as a public network service (SaaS), you must make the source code available under the AGPL terms.

## Part 1 Structure
- `backend/`: FastAPI application handling logic, centralized embeddings (MiniLM-L6-v2), Qdrant vector retrieval, and LLM orchestration (Gemini-3.5-flash).
- `frontend/`: React, TypeScript, Vite, Tailwind CSS v3.4 app implementing the workspace and role switcher dashboard.

## Quick Start
1. Copy `.env.example` to `.env` in the root:
   ```bash
   cp .env.example .env
   ```
   *Ensure you populate the `GEMINI_API_KEY`.*
2. Start the services:
   ```bash
   docker-compose up --build
   ```
3. Run migrations on startup (if not automatic):
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
