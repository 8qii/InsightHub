# InsightHub Case Study

## Problem

Business answers are often split between policy documents, operational spreadsheets, and transactional databases. A useful analyst must combine those sources while showing where the answer came from and how the request was executed.

## Solution

InsightHub presents one web analyst for Nova Retail Distribution. The user asks a natural-language question, the FastAPI intelligence service routes it through a bounded tool-calling loop, and the result returns with citations and structured business evidence. A lightweight executive dashboard exposes the same sales, inventory, and discount APIs for a fast operational read.

The Phase 7 interface streams the answer over Server Sent Events and then loads a metadata-only run trace. The trace shows tool names, durations, and statuses without exposing prompts, document contents, secrets, or database records.

## Architecture Decisions

- AnythingLLM remains the document ingestion and RAG shell rather than being forked.
- FastAPI owns the custom analyst orchestration and typed business tools.
- PostgreSQL access stays read-only and behind explicit application services.
- DuckDB and file analytics remain separate from document retrieval.
- One bounded orchestrator is preferred over a distributed multi-agent system.
- Next.js provides a focused product surface without adding a heavy BI framework.
- CSS-based dashboard charts keep the demo lightweight and easy to deploy.
- SSE adds progressive answer delivery without changing the existing JSON query contract.
- Trace storage is bounded and process-local to keep deployment simple and avoid a new persistence dependency.

## Tradeoffs

The trace registry is intentionally short-lived and is cleared when the intelligence process restarts. This is appropriate for a public portfolio demo; durable trace history would require an explicit storage decision later.

Streaming currently executes the existing agent run and emits the completed answer in small SSE chunks. It provides progressive UI delivery without introducing a second model execution path or changing tool orchestration. True provider-token streaming can be added later if the model gateway contract supports safe tool-call streaming.

The dashboard focuses on a few decision-relevant KPIs rather than attempting to become a general BI product. This keeps the demo understandable, testable, and deployable on modest infrastructure.
