# Model Provider

InsightHub keeps model execution behind AnythingLLM during Phase 1.5. AnythingLLM owns chat orchestration, document retrieval, embeddings, and managed vector storage; InsightHub only calls the AnythingLLM Developer API.

```text
AnythingLLM
    |
    | OpenAI-compatible API
    v
GPT-5.6 Luna
```

## Configuration Boundary

Configure the model in the AnythingLLM UI under the LLM provider settings:

- Provider: OpenAI Compatible
- Base URL: the OpenAI-compatible endpoint reachable from the AnythingLLM container
- Model: `gpt-5.6-luna`
- API key: configure locally in AnythingLLM; never commit it

The corresponding AnythingLLM provider identifier is `generic-openai`. Compose maps the canonical `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` variables to that provider when they are supplied.

For the local setup described in this repository, the endpoint is expected at `http://host.docker.internal:8317/v1`. The host name is intentionally documented here without any credential or private key.

Embedding configuration is also owned by AnythingLLM. Select a supported embedding provider and model in the AnythingLLM UI before indexing documents. The selected provider and model must be recorded in the Phase 1.5 validation report; InsightHub does not implement a custom embedding pipeline.
