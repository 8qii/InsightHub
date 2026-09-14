# InsightHub

InsightHub is an enterprise Knowledge & Data Agent for answering business questions across documents and structured data. It will combine an OSS knowledge shell with custom, traceable intelligence for analytics and mixed-source reasoning.

## Current Phase

Phase 0 is complete infrastructure only: the FastAPI service bootstrap, health checks, safe error handling, request tracing, local tooling, Docker, and CI. No AI, RAG, ingestion, database, or analytics features are implemented yet.

## Architecture

```text
AnythingLLM
    |
    v
FastAPI Intelligence Service
```

AnythingLLM integration is planned for a later phase. The Intelligence Service currently runs independently.

## Local Setup

Requires Python 3.12.

```bash
cd services/intelligence
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

```bash
cp ../../.env.example ../../.env
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps -e .
uvicorn app.main:app --reload
```

The service is available at `http://127.0.0.1:8000`. Check `GET /health/live` and `GET /health/ready`.

Run quality checks from `services/intelligence`:

```bash
ruff check .
mypy app
pytest
```

Run the containerized service from the repository root:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

## Configuration

Copy `.env.example` to `.env` and adjust the core application settings as needed. The AnythingLLM, LLM, PostgreSQL, and Langfuse variables are documented placeholders only; they are optional and unused during Phase 0.
