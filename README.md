# InsightHub

InsightHub is an enterprise AI analyst for answering business questions across company knowledge and structured data. It combines document retrieval, read-only business tools, citations, evaluation, and an executive web interface in one understandable deployment.

## Product Overview

Ask questions such as:

> Why did Product Luna revenue decline in Q3?

InsightHub can connect the Q3 business review, sales summaries, and historical inventory risk to produce an answer with source citations and a sanitized execution trace. It is built around the fictional Nova Retail Distribution business so cross-source facts remain coherent and demonstrable.

## Architecture

```text
Browser
   |
Next.js Web Analyst
   |  same-origin proxy, SSE, Markdown, charts
   v
FastAPI Intelligence Service
   |\
   | \-- Bounded AI Analyst Agent
   |     |-- Knowledge Search -> AnythingLLM
   |     |-- Sales Analytics -> PostgreSQL
   |     |-- Inventory Risk -> PostgreSQL
   |     \-- Discount Controls -> PostgreSQL
   |
   \-- Metadata-only Run Trace API
```

AnythingLLM remains an external OSS component. InsightHub does not fork its internals. The custom engineering boundary is the FastAPI intelligence service, typed tools, read-only data access, evaluation system, observability metadata, and web product.

## Screenshots

Screenshots are reserved for the hosted demo capture:

```text
[ Analyst chat screenshot placeholder ]
[ Executive dashboard screenshot placeholder ]
```

## Engineering Highlights

- Bounded tool-calling agent with explicit typed contracts.
- RAG for policy and business documents through AnythingLLM.
- Read-only PostgreSQL business services with SQL safety boundaries.
- Metadata-only agent traces with run IDs, tool durations, and status.
- Server Sent Events for progressive answer delivery without breaking the JSON API.
- Deterministic evaluation dataset covering routing, facts, sources, clarification, and recovery.
- Lightweight CSS dashboard charts without a heavy BI dependency.
- Docker Compose deployment suitable for a modest VPS.
- No provider credentials or database secrets in the frontend.

## Local Demo

Requires Python 3.12, Node.js 22, and Docker.

```bash
cp .env.example .env
docker compose --env-file .env -f deployment/docker-compose.yml up --build
```

Open:

- Web analyst: `http://localhost:3000`
- Executive dashboard: `http://localhost:3000/dashboard`
- FastAPI health: `http://localhost:8000/health/live`
- AnythingLLM: `http://localhost:3001`

Configure `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, and `ANYTHINGLLM_API_KEY` in the uncommitted `.env`. Never commit `.env`.

Try:

```text
Why did Product Luna revenue decline in Q3?
```

Expected evidence includes an 18% decline from `$300,000` in Q2 to `$246,000` in Q3, 138-day inventory, and a `q3_business_review.md` citation.

## API Surface

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/agent/query` | Existing JSON agent contract |
| `POST` | `/api/v1/agent/query/stream` | SSE answer delivery |
| `GET` | `/api/v1/agent/runs/{run_id}` | Metadata-only execution trace |
| `GET` | `/api/v1/data/sales/summary` | Sales summary |
| `GET` | `/api/v1/data/inventory/risk` | Aging inventory |
| `GET` | `/api/v1/data/discount/violations` | Discount controls |

## Quality Checks

Backend, from `services/intelligence`:

```bash
ruff check .
mypy app
pytest
```

Frontend, from `apps/web`:

```bash
npm install
npm run lint
npm run build
```

Compose validation:

```bash
docker compose --env-file .env -f deployment/docker-compose.yml config
docker compose --env-file .env -f deployment/docker-compose.yml up --build
```

See [production deployment](docs/deployment/production.md) and the [case study](docs/case-study.md) for architecture, operations, and tradeoffs.
