# InsightHub

InsightHub is an enterprise Knowledge & Data Agent for answering business questions across documents and structured data. It will combine an OSS knowledge shell with custom, traceable intelligence for analytics and mixed-source reasoning.

## Current Phase

Phase 4 adds a lightweight AI Analyst Agent. AnythingLLM owns document ingestion, indexing, embeddings, workspace management, managed vector storage, and knowledge retrieval. InsightHub owns the bounded agent loop, typed business tools, PostgreSQL access, citations, and evaluation.

## Architecture

```text
AnythingLLM
    | Developer API
    v
FastAPI Intelligence Service
    |\
    | \-- OpenAI-compatible Analyst Agent
    |     |-- search_company_knowledge
    |     |-- get_sales_summary
    |     |-- get_inventory_risk
    |     \-- get_discount_violations
    |
    \-- Typed PostgreSQL business tools
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
docker compose --env-file .env -f deployment/docker-compose.yml up --build
```

This starts AnythingLLM at `http://127.0.0.1:3001` and InsightHub at `http://127.0.0.1:8000`.

## Phase 1.5 AnythingLLM Setup

1. Open `http://127.0.0.1:3001` and complete AnythingLLM's initial setup.
2. Configure the OpenAI-compatible LLM provider using `http://host.docker.internal:8317/v1` and model `gpt-5.6-luna`.
3. Configure a supported embedding provider and model in AnythingLLM.
4. Create the `insighthub-demo` workspace and upload the documents in `demo/company/`.
5. Create a Developer API key. The instance API documentation is available at `http://127.0.0.1:3001/api/docs`.
6. Copy `.env.example` to `.env` and set `ANYTHINGLLM_API_KEY` locally. Never commit `.env`.

Follow `docs/testing/rag-validation.md` for the two real RAG questions and expected citations.

Query the configured workspace through InsightHub:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/knowledge/query \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: phase1-demo" \
  -d '{"workspace_id":"insighthub-demo","query":"What is the maximum VIP discount?"}'
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/knowledge/query `
  -ContentType "application/json" `
  -Headers @{ "X-Request-ID" = "phase1-demo" } `
  -Body '{"workspace_id":"insighthub-demo","query":"What is the maximum VIP discount?"}'
```

## Agent Query

The agent endpoint is available at `POST /api/v1/agent/query`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the maximum VIP discount allowed?"}'
```

Configure `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, and `ANYTHINGLLM_WORKSPACE_ID` in the uncommitted `.env`. The model is never hardcoded in the runtime. The agent does not execute arbitrary SQL or access PostgreSQL directly.

## Configuration

Copy `.env.example` to `.env` and adjust the core application settings as needed. `ANYTHINGLLM_BASE_URL`, `ANYTHINGLLM_API_KEY`, and `ANYTHINGLLM_TIMEOUT_SECONDS` configure the knowledge adapter. `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` configure the OpenAI-compatible analyst decision layer. Never commit `.env`.
