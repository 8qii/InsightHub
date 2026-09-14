# Context

InsightHub needs document retrieval and citation-backed answers without duplicating a mature RAG stack. AnythingLLM provides the required document, workspace, embedding, vector, and chat capabilities through its Developer API.

# Decision

Treat AnythingLLM as an external knowledge service and integrate it through a small adapter boundary in the FastAPI service. Use the pinned `mintplexlabs/anythingllm:1.16.1@sha256:05617e7bece7fd6eddc4f5b4176cd87fff74d7da88d988a6109b95481cce122c` image. Normalize its response into provider-independent InsightHub source models and use the verified `mode: "query"` workspace chat contract.

# Alternatives Considered

Vendoring or deeply forking AnythingLLM would make upstream upgrades difficult and blur ownership. Implementing a custom parser, chunker, embedding pipeline, and vector store would duplicate commodity functionality and expand Phase 1 beyond its objective.

# Consequences

InsightHub remains independently testable and does not expose upstream response formats. The integration depends on the documented AnythingLLM Developer API and requires an AnythingLLM-configured LLM, embedding provider, workspace, and API key for live RAG.
