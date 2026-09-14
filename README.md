# InsightHub

InsightHub is an enterprise Knowledge & Data Agent for answering business questions across documents and structured data. It will combine an OSS knowledge shell with custom, traceable intelligence for analytics and mixed-source reasoning.

## Current Phase

Phase 1 adds the AnythingLLM runtime integration and RAG baseline. AnythingLLM owns document ingestion, indexing, embeddings, workspace management, and RAG generation. InsightHub exposes a normalized knowledge query API. Structured-data and agent features are not implemented.

## Architecture

```text
AnythingLLM
    | Developer API
    v
FastAPI Intelligence Service
```

AnythingLLM remains an external OSS component; InsightHub does not fork its internals.

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

Run the Phase 1 stack from the repository root:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

This starts AnythingLLM at `http://127.0.0.1:3001` and InsightHub at `http://127.0.0.1:8000`.

## Phase 1 AnythingLLM Setup

1. Open `http://127.0.0.1:3001` and complete AnythingLLM's initial setup.
2. Configure one LLM provider and one embedding provider in AnythingLLM.
3. Create a workspace and upload a small non-sensitive PDF or DOCX.
4. Create a Developer API key. The instance API documentation is available at `http://127.0.0.1:3001/api/docs`.
5. Copy `.env.example` to `.env` and set `ANYTHINGLLM_API_KEY` locally. Never commit `.env`.

Query the configured workspace through InsightHub:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/knowledge/query \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: phase1-demo" \
  -d '{"workspace_id":"insighthub-phase1","query":"What is the maximum VIP discount?"}'
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/knowledge/query `
  -ContentType "application/json" `
  -Headers @{ "X-Request-ID" = "phase1-demo" } `
  -Body '{"workspace_id":"insighthub-phase1","query":"What is the maximum VIP discount?"}'
```

## Configuration

Copy `.env.example` to `.env` and adjust the core application settings as needed. `ANYTHINGLLM_BASE_URL`, `ANYTHINGLLM_API_KEY`, and `ANYTHINGLLM_TIMEOUT_SECONDS` are used by the Phase 1 adapter. The remaining LLM, PostgreSQL, and Langfuse variables remain future placeholders.
