# 006 Lightweight Analyst Agent

## Context

InsightHub needs an AI reasoning layer that combines the existing AnythingLLM knowledge adapter with the existing typed PostgreSQL business tools. A general agent framework would add infrastructure and obscure the tool contracts needed for evaluation and debugging.

## Decision

Implement a small internal runtime with four boundaries:

```text
Question
  -> Agent Loop
  -> OpenAI-compatible decision client
  -> Typed Tool Registry and Executor
  -> Existing Knowledge/Data Services
  -> Final Answer with citations
```

The model receives OpenAI-compatible function schemas. Every tool validates arguments with Pydantic, executes with a timeout, and returns structured JSON. The runtime supports multiple tool calls, bounded iterations, safe tool errors, and request-correlated logs.

## Alternatives

- LangChain, LangGraph, CrewAI, and AutoGen: rejected because they add framework behavior and dependencies not required for the V1 loop.
- Direct database access from the model: rejected because PostgreSQL access must remain behind the existing typed services.
- A second knowledge implementation: rejected because AnythingLLM remains the document retrieval system.

## Consequences

The agent is easy to test with a fake LLM protocol and existing service fakes. The model is constrained to four explicit tools, but future tools can be added through the registry without changing the loop. Tool selection quality remains model-dependent and is covered by the evaluation dataset.
