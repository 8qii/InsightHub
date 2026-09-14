# Production Deployment

InsightHub is designed for a small single-host deployment using Docker Compose, a reverse proxy, and hosted model APIs. Kubernetes and separate microservices are not required for the portfolio deployment.

## Services

| Service | Purpose | Internal port | Published port |
| --- | --- | ---: | ---: |
| `web` | Next.js analyst interface | 3000 | 3000 |
| `intelligence` | FastAPI agent, tools, traces | 8000 | 8000 |
| `anythingllm` | RAG and document workspace | 3001 | 3001 |
| `postgres` | Read-only business data source | 5432 | 5432 |

In production, expose the web service through Caddy or Nginx and keep the API, AnythingLLM, and PostgreSQL ports private to the host/network.

## Environment Variables

Copy `.env.example` to `.env` and provide deployment values. Never commit `.env`.

Required:

- `POSTGRES_PASSWORD`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `ANYTHINGLLM_API_KEY`

Important application settings:

- `NEXT_PUBLIC_API_URL`: FastAPI URL used when building the web image. Compose defaults to `http://intelligence:8000`.
- `ANYTHINGLLM_BASE_URL`: defaults to `http://anythingllm:3001` inside Compose.
- `ANYTHINGLLM_WORKSPACE_ID`: RAG workspace, default `insighthub-demo`.
- `INTELLIGENCE_PORT`: host port for FastAPI, default `8000`.
- `WEB_PORT`: host port for Next.js, default `3000`.
- `LANGFUSE_ENABLED`: observability switch, default `false`.

## Deployment Steps

1. Install Docker Engine and Docker Compose on the host.
2. Clone the repository and create `.env` from `.env.example`.
3. Configure the hosted OpenAI-compatible model and AnythingLLM workspace.
4. Start the stack:

```bash
docker compose --env-file .env -f deployment/docker-compose.yml up -d --build
```

5. Check service state:

```bash
docker compose --env-file .env -f deployment/docker-compose.yml ps
```

6. Verify the public web service at `http://localhost:3000` and the intelligence health endpoint at `http://localhost:8000/health/live`.
7. Put a TLS reverse proxy in front of port `3000` before exposing the demo publicly.

## Operational Notes

The run trace API stores a bounded number of metadata-only records in process memory. It exposes run ID, status, tool names, durations, and no prompts, documents, secrets, or database rows. Restarting the intelligence container clears this short-lived inspection history.

The frontend uses a same-origin `/backend` rewrite. The Compose build passes `NEXT_PUBLIC_API_URL` as a build argument so the server-side rewrite reaches the `intelligence` service on the Compose network.

Back up the PostgreSQL and AnythingLLM volumes according to the deployment host's backup policy. Do not put API keys in browser code, frontend environment files, or logs.
