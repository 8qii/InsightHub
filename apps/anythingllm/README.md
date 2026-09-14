# AnythingLLM Runtime

InsightHub uses AnythingLLM as an external OSS knowledge, document-ingestion, workspace, embedding, and RAG runtime. InsightHub does not vendor or modify AnythingLLM source code.

## Upstream

- Project: <https://github.com/Mintplex-Labs/anything-llm>
- License: MIT
- Runtime image: `mintplexlabs/anythingllm:1.16.1@sha256:05617e7bece7fd6eddc4f5b4176cd87fff74d7da88d988a6109b95481cce122c`
- Documentation: <https://docs.anythingllm.com>
- Developer API documentation: `http://localhost:3001/api/docs` after startup

The versioned image tag is used instead of `latest`, which is updated frequently. Upgrade the tag deliberately and re-verify the API contract.

## Persistence

Compose mounts the named volume `anythingllm-storage` at `/app/server/storage`. This stores AnythingLLM configuration, workspaces, document state, and local vector data across container restarts.

## Initial Setup

1. Start the stack with `docker compose --env-file .env -f deployment/docker-compose.yml up -d`.
2. Open <http://localhost:3001> and complete the initial setup.
3. Select an LLM provider and embedding provider in AnythingLLM.
4. Create a workspace and upload a non-sensitive document.
5. Create a Developer API key in AnythingLLM.
6. Put that key in the local, uncommitted `.env` as `ANYTHINGLLM_API_KEY`.

## LLM Setup

Configure the LLM in AnythingLLM's provider settings:

- Provider: `OpenAI Compatible`
- Base URL: `http://host.docker.internal:8317/v1`
- Model: `gpt-5.6-luna`
- API key: configure locally in AnythingLLM; do not commit it

`host.docker.internal` is required when AnythingLLM runs in Docker. `localhost` would refer to the AnythingLLM container itself, not the host machine where the OpenAI-compatible endpoint is running.

The Compose file also maps the canonical `.env.example` values `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` to AnythingLLM's `generic-openai` environment settings. This makes a non-interactive local setup reproducible; the values remain blank in the committed template.

## Embedding Setup

Configure embeddings in AnythingLLM before uploading documents. The default Phase 1.5 setup uses AnythingLLM's managed native embedder with model `Xenova/all-MiniLM-L6-v2`. The Compose file maps `EMBEDDING_MODEL` to AnythingLLM's `EMBEDDING_MODEL_PREF` setting. If the model is changed, select a supported provider and model in the installed version's embedding settings, then wait for indexing to complete.

Record the actual embedding provider and model used for a validation run in the report described by `docs/testing/rag-validation.md`. The embedding model must be compatible with the selected provider and must not be assumed to be `gpt-5.6-luna`.

## Developer API Contract Used

The adapter uses the v1.16.1 Developer API:

- Authentication validation: `GET /api/v1/auth`
- Workspace query: `POST /api/v1/workspace/{workspace_slug}/chat`
- Header: `Authorization: Bearer <developer-api-key>`
- Body: `{"message": "...", "mode": "query", "reset": false}`
- Response fields: `textResponse` and `sources[]`

`query` mode uses workspace retrieval and does not invoke AnythingLLM agent mode or web tools. InsightHub normalizes source `title`, `url`/`uri`, `chunk`/`text`, `score`, and `page` only when present.

## Responsibility Boundary

AnythingLLM owns document ingestion, parsing, chunking, embedding, vector storage, workspace management, and RAG generation. InsightHub owns the HTTP adapter, provider-independent models, safe errors, request tracing, latency metadata, and normalized API response.
