# AGENTS.md — InsightHub Project Alignment Guide

This file is the persistent instruction set for any AI coding agent working on InsightHub.

Agents must read this file before making architectural, implementation, refactoring, dependency, or deployment decisions.

---

# 1. Project Mission

Build **InsightHub**, an enterprise-general Knowledge & Data Agent that can reason across:

- PDF
- DOCX
- Excel
- CSV
- PostgreSQL

The product should answer business questions using both unstructured and structured sources and return:

- answer
- citations
- structured data evidence
- optional chart
- execution trace

This is a portfolio-grade project intended to demonstrate:

- AI engineering
- backend engineering
- web/product engineering
- data engineering
- system design
- production awareness

---

# 2. Core Priorities

All decisions must optimize for the following order:

1. Strong technical demonstration
2. Fast development
3. Clear, maintainable architecture
4. Low deployment complexity
5. Low operating cost
6. Easy debugging and evaluation
7. Future extensibility

Do not optimize for hypothetical enterprise scale before V1 works.

---

# 3. V1 Scope

Supported sources:

- PDF
- DOCX
- Excel
- CSV
- PostgreSQL

Supported core capabilities:

- RAG over documents
- citations
- spreadsheet analytics
- PostgreSQL analytics
- query/tool routing
- mixed-source reasoning
- chart generation
- evaluation
- query inspection
- observability

---

# 4. Explicit Non-Goals for V1

Do not implement unless explicitly requested by the human owner:

- Google Drive
- Notion
- Jira
- Slack
- Confluence
- billing
- SaaS multi-tenancy
- Kubernetes
- Kafka
- Spark
- Airflow
- self-hosted production LLM
- custom authentication
- mobile app
- fine-tuning
- complex workflow builder
- unnecessary microservices
- large multi-agent frameworks
- custom vector database

If a feature request risks expanding into one of these, stop and propose the smallest compatible alternative.

---

# 5. OSS Boundary

Use OSS for commodity functionality.

Current base direction:

- AnythingLLM for:
  - chat UI
  - document ingestion
  - chunking
  - embeddings
  - vector/RAG layer
  - citations
  - basic workspace/chat functionality

Do not deeply fork or scatter modifications throughout OSS internals unless absolutely necessary.

Prefer integration through:

- APIs
- adapters
- extension modules
- separate services

---

# 6. Custom Ownership

The project must clearly own these components:

- FastAPI Intelligence Service
- Agent Router
- DuckDB Data Engine
- PostgreSQL Tool
- SQL Safety Layer
- Cross-Source Reasoning
- Data Profiling
- Data Explorer
- Chart Specification
- Evaluation Framework
- Query Inspector
- Observability Integration
- CI/CD
- Project Architecture

When adding functionality, prefer placing it in custom project code rather than patching OSS core.

---

# 7. Architecture Principle

Preferred architecture:

```text
AnythingLLM
    │
    ▼
FastAPI Intelligence Service
    │
    ├── Knowledge Tool
    ├── DuckDB Tool
    └── PostgreSQL Tool
    │
    ▼
LLM Reasoning
```

Use one orchestrator with explicit tools.

Do not introduce a distributed multi-agent system unless evaluation proves it is required.

---

# 8. Repository Boundaries

Preferred custom code location:

```text
services/intelligence/
```

Preferred submodules:

```text
app/
  api/
  agents/
  tools/
  data/
  evaluation/
  security/
  observability/
  models/
```

Demo data:

```text
demo/
```

Evaluation data:

```text
evaluation/
```

Architecture docs:

```text
docs/
```

Deployment:

```text
deployment/
```

Keep unrelated concerns separate.

---

# 9. Coding Style

## General

Prefer:

- simple code
- explicit types
- small modules
- clear interfaces
- typed structured outputs
- deterministic behavior where possible

Avoid:

- magic
- hidden side effects
- giant classes
- giant prompts
- giant service modules
- premature abstraction

## Python

Use:

- type hints
- Pydantic models for API/tool boundaries
- async only where it improves I/O behavior
- explicit exceptions
- clear logging

Prefer small functions over deep inheritance trees.

---

# 10. Tool Contract Rule

Every AI tool must expose a clear typed contract.

Example:

```python
class QueryResult(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    execution_ms: int
```

Do not return arbitrary prose from a tool when structured data is possible.

The LLM should receive structured tool output and perform reasoning afterward.

---

# 11. SQL Safety Rules

PostgreSQL access is read-only.

Never allow the agent to execute:

- INSERT
- UPDATE
- DELETE
- DROP
- ALTER
- TRUNCATE
- CREATE
- GRANT
- REVOKE

Required controls:

- read-only DB role
- SQL validation
- statement timeout
- row limit
- schema allowlist
- result size limit

If SQL safety cannot be guaranteed, fail closed.

Do not silently execute suspicious SQL.

---

# 12. Structured vs Unstructured Data

Do not treat every source as RAG text.

Use:

```text
PDF/DOCX
→ parse
→ chunk
→ embed/index
→ RAG
```

Use:

```text
Excel/CSV
→ DuckDB
→ schema/profile/query
```

Use:

```text
PostgreSQL
→ schema context
→ validated read-only SQL
```

Combine sources only at orchestration/synthesis time.

---

# 13. LLM Usage Rules

Use LLMs for:

- intent classification
- reasoning
- SQL generation
- answer synthesis
- chart recommendation
- query reformulation when useful

Do not use LLMs for tasks that are better deterministic:

- MIME detection
- schema inference
- SQL safety validation
- metric calculations
- file validation
- chart schema validation

---

# 14. Prompt Design Rules

Avoid one giant prompt.

Separate prompts by responsibility:

- route query
- generate SQL
- synthesize answer
- evaluate answer

Prompts should be:

- small
- versioned
- testable
- easy to inspect

If a prompt grows too large, split responsibility.

---

# 15. Agent Routing

Supported intents:

```text
knowledge
tabular
database
mixed
```

Default behavior:

- prefer the smallest sufficient tool set
- avoid unnecessary tool calls
- allow mixed-source execution when required

Do not call every tool for every query.

---

# 16. Chart Rules

The LLM may propose a chart, but it must return a typed specification.

Example:

```json
{
  "type": "bar",
  "title": "Revenue by region",
  "x": "region",
  "y": "revenue"
}
```

Frontend is responsible for rendering.

Never execute arbitrary JavaScript/HTML generated by the LLM.

---

# 17. Evaluation First

Any important AI behavior should have evaluation coverage.

Golden dataset should test:

- routing
- source selection
- SQL correctness
- numerical correctness
- citations
- mixed-source reasoning

Do not add a new connector before core evaluation quality is acceptable.

---

# 18. Evaluation Rules

Prefer deterministic checks where possible.

Good checks:

- expected SQL result
- expected source ID
- expected number/range
- expected tool usage
- expected category

LLM-as-a-judge may supplement but should not be the only scoring method.

---

# 19. Observability

Every production-like query should be traceable.

Track:

- request ID
- selected intent
- selected tools
- tool latency
- LLM latency
- model
- token count
- estimated cost
- failures

Use Langfuse Cloud initially.

Do not self-host observability infrastructure unless necessary.

---

# 20. Performance Rules

Do not optimize blindly.

Measure before adding:

- Redis
- caching
- queues
- parallel execution
- batching

Start simple.

Optimize real bottlenecks.

---

# 21. Cost Rules

V1 should avoid GPU infrastructure.

Prefer hosted model APIs.

Expected demo-level operating budget:

```text
~$15–45/month
```

Do not introduce infrastructure that materially increases this without explicit approval.

---

# 22. Deployment Rules

V1 deployment target:

```text
single VPS
+
Docker Compose
+
Caddy/Nginx
+
hosted LLM
```

Do not introduce Kubernetes.

Deployment should be understandable and reproducible.

Target experience:

```bash
docker compose up -d
```

---

# 23. Dependency Rules

Before adding a dependency, ask:

1. Is this problem already solved by the current stack?
2. Can it be implemented simply without a new dependency?
3. Is the dependency actively maintained?
4. Does it materially increase infrastructure complexity?
5. Does it improve portfolio value?

Avoid dependencies added only for convenience.

---

# 24. Refactoring Rules

Do not perform broad refactors unrelated to the current task.

Avoid:

- renaming entire modules for style
- replacing framework choices without need
- rewriting working OSS components
- speculative abstraction

Small, localized refactors are preferred.

---

# 25. Backward Compatibility

Before modifying:

- public API
- DB schema
- tool contracts
- evaluation dataset format

check whether existing tests and integrations depend on them.

Document intentional breaking changes.

---

# 26. Error Handling

Errors should:

- fail safely
- include a traceable request ID
- provide useful logs
- avoid leaking secrets
- return human-readable API errors

Never swallow exceptions silently.

---

# 27. Security

Never commit:

- API keys
- DB passwords
- access tokens
- `.env`
- production secrets

Always maintain:

```text
.env.example
```

Uploads must have:

- file size limits
- extension checks
- MIME validation where practical
- safe filenames

---

# 28. Demo Dataset Rules

Use one coherent fictional business:

**Nova Retail Distribution**

Do not create random independent datasets.

Cross-source facts should agree.

Example:

If Product C sales decline in Excel, PostgreSQL and business documents should support the same story.

The demo should prove reasoning across sources, not just data ingestion.

---

# 29. Main Demo Scenarios

The project should always preserve at least these scenarios.

## Scenario A — Knowledge

> What is the VIP discount policy?

Expected:
- document RAG
- citation

## Scenario B — Data

> What was Q3 revenue by region?

Expected:
- spreadsheet or SQL query
- result table
- optional chart

## Scenario C — Mixed

> What is the maximum VIP discount, how much Q3 VIP revenue did we generate, and how many orders violated the policy?

Expected:
- knowledge retrieval
- SQL/data query
- synthesis
- citations
- numerical evidence

Scenario C is the primary showcase.

---

# 30. Testing Requirements

Every feature should add appropriate tests.

Minimum expectations:

### Unit
- validators
- profiler
- routing parser
- chart schema
- SQL safety

### Integration
- DuckDB
- PostgreSQL
- knowledge API adapter

### Evaluation
- golden dataset

### E2E
- knowledge query
- database query
- mixed query

Do not merge major features with no test coverage.

---

# 31. Definition of Done for a Feature

A feature is complete only when:

- implementation works
- error cases handled
- tests pass
- typed interfaces are stable
- logging exists
- docs updated if architecture changes
- evaluation added if AI behavior changed

"Code compiles" is not sufficient.

---

# 32. Architecture Decision Records

When making a significant architectural change, create an ADR.

Format:

```text
Context
Decision
Alternatives
Consequences
```

Examples:

```text
001-use-anythingllm-as-rag-shell.md
002-separate-fastapi-intelligence-service.md
003-use-duckdb-for-file-analytics.md
004-readonly-postgresql-agent.md
005-single-orchestrator-over-multi-agent.md
```

Agents should update or add ADRs for important decisions.

---

# 33. Change Management

Before large changes, summarize:

- what is changing
- why
- affected modules
- migration impact
- testing plan

For small changes, proceed directly.

Do not redesign the project silently.

---

# 34. Priority Order When Time Is Limited

Always prioritize:

1. Mixed-source reasoning
2. SQL/Data Agent quality
3. Evaluation
4. Data Explorer
5. Charts
6. Query Inspector
7. Observability
8. New connectors

Never trade core quality for breadth.

---

# 35. V1 Exit Criteria

Do not call V1 complete unless:

- PDF/DOCX RAG works
- Excel/CSV analysis works
- PostgreSQL analysis works
- source routing works
- mixed-source reasoning works
- citations work
- SQL is read-only and validated
- Data Explorer exists
- chart generation works
- evaluation suite exists
- query trace exists
- deployment works with Docker Compose
- project runs on modest VPS resources
- README clearly separates OSS vs custom work

---

# 36. Agent Workflow

When starting a task:

1. Read this file.
2. Read ROADMAP.md.
3. Inspect relevant code before proposing changes.
4. Preserve current architecture unless a clear reason exists.
5. Implement the smallest complete solution.
6. Add/update tests.
7. Update documentation if architecture or behavior changed.
8. Avoid scope expansion.

When uncertain, prefer the option that:

- adds less infrastructure
- is easier to evaluate
- is easier to debug
- preserves OSS upgradeability
- keeps operating cost low

---

# 37. Never Do These Without Explicit Human Approval

- replace AnythingLLM
- replace FastAPI
- replace DuckDB
- introduce Kubernetes
- introduce Kafka
- introduce a vector database migration
- introduce microservices beyond the current architecture
- move to local GPU inference
- add multi-tenancy
- add billing
- perform a broad OSS fork rewrite
- add autonomous write actions against business databases
- relax SQL safety

---

# 38. Guiding Principle

The project should look like the work of an engineer who understands where **not** to write code.

Reuse commodity infrastructure.

Build custom intelligence where it creates technical value.

Measure AI quality.

Keep the system understandable.

Ship early.

Improve depth before breadth.
