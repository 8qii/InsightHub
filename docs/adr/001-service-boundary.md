# Context

InsightHub needs a knowledge/chat experience as well as custom structured-data intelligence. AnythingLLM already provides the commodity document, RAG, citation, workspace, and chat capabilities needed by the project.

# Decision

Use AnythingLLM as the OSS knowledge and chat layer. Keep InsightHub-specific intelligence in a separate FastAPI service, connected through APIs in a later phase. Avoid deep modifications to AnythingLLM internals.

# Alternatives Considered

Forking and extending AnythingLLM directly would couple custom behavior to OSS internals. Building every knowledge and chat capability in the FastAPI service would duplicate mature commodity functionality.

# Consequences

The FastAPI service has an independently testable and deployable boundary. AnythingLLM remains upgradeable, while InsightHub retains clear ownership of its future routing, data, safety, evaluation, and observability capabilities.
