# Local Development Environment

InsightHub uses two environment files:

- `.env.example` is the committed, secret-free configuration reference.
- `.env` is the local developer configuration and is ignored by Git.

Never commit `.env`, `.env.local`, API keys, tokens, or passwords. If a credential is exposed, revoke it and replace it locally.

## New Developer Setup

1. Copy the template:

   ```bash
   cp .env.example .env
   ```

2. Set the local AnythingLLM Developer API key in `ANYTHINGLLM_API_KEY`.
3. Set the local OpenAI-compatible endpoint credentials in `LLM_BASE_URL` and `LLM_API_KEY`.
4. Keep `LLM_MODEL=gpt-5.6-luna` unless the local endpoint uses another configured model.
5. Keep `EMBEDDING_PROVIDER=anythingllm-native` and `EMBEDDING_MODEL=Xenova/all-MiniLM-L6-v2` for the supported local RAG setup.
6. Validate the resolved Compose configuration:

   ```bash
   docker compose --env-file .env -f deployment/docker-compose.yml config
   ```

7. Start the services:

   ```bash
   docker compose --env-file .env -f deployment/docker-compose.yml up -d
   ```

8. Open AnythingLLM at `http://127.0.0.1:3001` and confirm the `insighthub-demo` workspace and documents are present.
9. Verify InsightHub at `http://127.0.0.1:8000/health/ready`.

## Required Variables

Application:

- `APP_NAME`
- `APP_ENV`
- `LOG_LEVEL`

AnythingLLM:

- `ANYTHINGLLM_BASE_URL`
- `ANYTHINGLLM_API_KEY`
- `ANYTHINGLLM_TIMEOUT_SECONDS`

LLM:

- `LLM_PROVIDER`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`

Embedding:

- `EMBEDDING_PROVIDER`
- `EMBEDDING_MODEL`

Storage and feature placeholders are documented in `.env.example`; PostgreSQL, DuckDB, evaluation, and Langfuse are not enabled by this local RAG setup.

## Provider Mapping

The project-facing provider value is `openai-compatible`. Docker Compose maps that configuration to AnythingLLM's `generic-openai` provider and passes the base URL, key, and model through the corresponding AnythingLLM variables.

Because the Compose file is stored under `deployment/`, pass the root `.env` explicitly with `--env-file .env` when running Compose from the repository root.

Inside the AnythingLLM container, the host model endpoint must use `host.docker.internal`, not `localhost`.
