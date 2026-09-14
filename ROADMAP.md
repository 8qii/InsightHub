# InsightHub — Enterprise Knowledge & Data Agent
## Detailed Roadmap, Architecture, Delivery Plan, and Engineering Notes

> Goal: Build a portfolio-grade, enterprise-general AI platform that combines unstructured knowledge and structured business data to produce traceable answers, analytics, charts, and reports.
>
> Core priorities:
> 1. Strong technical impression
> 2. Fast development using existing open-source code
> 3. Easy local development and deployment
> 4. Low operating cost
> 5. Clear separation between reused OSS and custom engineering
> 6. Avoid unnecessary enterprise complexity in V1

---

# 1. Product Definition

## 1.1 Product name

**InsightHub — Enterprise Knowledge & Data Agent**

Temporary/internal naming is acceptable during development.

## 1.2 Product positioning

InsightHub helps a business ask natural-language questions across:

- PDF
- DOCX
- Excel
- CSV
- PostgreSQL

The system automatically decides whether the question requires:

- knowledge retrieval
- spreadsheet analysis
- SQL access
- a combination of sources

It then returns:

- natural-language answer
- citations
- supporting rows/data
- optional charts
- source trace
- execution metadata

## 1.3 Example business question

> According to the current discount policy, what is the maximum discount for VIP customers? What was Q3 revenue from VIP customers, and how many orders exceeded the allowed discount?

Expected execution:

1. Search policy documents using RAG.
2. Extract allowed VIP discount.
3. Query customers/orders/payments in PostgreSQL.
4. Compare actual discounts against policy.
5. Produce a final answer with citations and calculated results.
6. Optionally render a chart or summary table.

This cross-source reasoning is the main showcase feature of V1.

---

# 2. Scope

## 2.1 V1 supported data sources

Only the following sources are required:

### Unstructured
- PDF
- DOCX

### Structured files
- Excel
- CSV

### Database
- PostgreSQL

These sources are sufficient to demonstrate AI, backend, web, data engineering, and system design.

## 2.2 Explicitly out of scope for V1

Do **not** implement the following in V1:

- Google Drive
- Notion
- Jira
- Slack
- Confluence
- Salesforce
- Billing
- Multi-tenant SaaS architecture
- Kubernetes
- Kafka
- Spark
- Airflow
- Self-hosted production LLM
- Custom authentication system
- Mobile application
- Fine-tuning
- Complex workflow builder
- Large multi-agent framework
- Custom vector database implementation

If time remains, improve quality and evaluation before adding more breadth.

---

# 3. OSS Strategy

## 3.1 Base platform

Use **AnythingLLM** as the initial OSS foundation for:

- chat UI
- document ingestion
- chunking
- embeddings
- vector/RAG pipeline
- workspace management
- source citations
- basic agent/chat infrastructure
- Docker deployment

Reasoning:

- MIT license
- existing RAG/chat UX
- quick bootstrap
- low infrastructure overhead
- suitable for portfolio deployments
- allows custom intelligence services to remain independent

## 3.2 Custom engineering layer

Build a separate **FastAPI Intelligence Service** instead of deeply modifying the OSS core.

Custom code should own:

- agent router
- source selection
- Excel/CSV engine
- DuckDB integration
- PostgreSQL read-only SQL agent
- SQL validation
- cross-source reasoning
- data profiling
- chart specification
- evaluation framework
- query inspector
- observability integration
- application-specific APIs

This separation prevents the project from looking like a simple fork.

---

# 4. High-Level Architecture

```text
                        ┌──────────────────────┐
                        │      Web / Chat      │
                        │      AnythingLLM     │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Intelligence Service │
                        │       FastAPI        │
                        └──────────┬───────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
                 ▼                 ▼                 ▼
        Knowledge Search      File Data Tool      SQL Tool
        AnythingLLM API         DuckDB           PostgreSQL
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   │
                                   ▼
                           LLM / Reasoning Layer
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
                  Answer          Chart          Report
                    │
                    ▼
                Citations
```

---

# 5. Technology Stack

## Frontend / product shell
- AnythingLLM UI initially
- Optional custom React/Next.js pages for:
  - Data Explorer
  - Evaluation Studio
  - Query Inspector
  - Analytics dashboard

## Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy where useful

## Structured data
- DuckDB
- PostgreSQL

## AI
- Hosted LLM API initially
- Hosted or lightweight embedding provider
- Do not require local GPU

## Observability
- Langfuse Cloud initially

## Infrastructure
- Docker Compose
- Caddy or Nginx
- single VPS
- GitHub Actions

## Optional later
- LiteLLM gateway
- Redis
- object storage

---

# 6. Repository Structure

Recommended structure:

```text
insighthub/
│
├── apps/
│   └── anythingllm/
│
├── services/
│   └── intelligence/
│       ├── app/
│       │   ├── api/
│       │   ├── agents/
│       │   ├── tools/
│       │   │   ├── knowledge.py
│       │   │   ├── duckdb_tool.py
│       │   │   └── postgres_tool.py
│       │   ├── data/
│       │   ├── evaluation/
│       │   ├── security/
│       │   ├── observability/
│       │   └── models/
│       └── tests/
│
├── demo/
│   ├── documents/
│   ├── spreadsheets/
│   ├── database/
│   └── seed/
│
├── evaluation/
│   ├── datasets/
│   ├── runners/
│   └── reports/
│
├── docs/
│   ├── architecture/
│   └── adr/
│
├── deployment/
│   └── docker-compose.yml
│
├── .github/
│   └── workflows/
│
├── ROADMAP.md
├── AGENTS.md
└── README.md
```

Keep custom code outside the OSS internals as much as possible.

---

# 7. Demo Business Dataset

Use one coherent fictional company instead of random test data.

Suggested business:

**Nova Retail Distribution**

## 7.1 Documents

```text
sales-policy.pdf
inventory-policy.docx
q3-business-plan.pdf
marketing-plan.docx
supplier-policy.pdf
customer-segmentation-policy.docx
```

## 7.2 Structured files

```text
sales_q3.xlsx
inventory.xlsx
marketing.csv
returns.csv
```

## 7.3 PostgreSQL schema

Suggested tables:

```text
customers
products
orders
order_items
payments
customer_segments
discount_events
```

Suggested scale:

- 10k–50k customers
- 50k–200k orders
- 500–2,000 products
- enough records to make aggregation meaningful

Do not create millions of rows in V1.

## 7.4 Data coherence

The same business story must appear across multiple sources.

Example:

Product C:
- sales down 18%
- stock up 42%
- marketing spend down 25%
- business plan marks it as strategic
- repeat purchase rate drops in PostgreSQL

This allows meaningful cross-source reasoning.

---

# 8. Development Roadmap

# Phase 0 — Scope Freeze
Estimated: 0.5 day

## Goals

- Confirm V1 scope.
- Create repository.
- Add ROADMAP.md and AGENTS.md.
- Define architectural boundaries.
- Add ADR structure.

## Deliverables

- repository initialized
- architecture diagram draft
- coding conventions
- branch strategy
- environment setup notes

## Important note

Do not begin adding integrations beyond the locked scope.

---

# Phase 1 — OSS Foundation
Estimated: 1–2 days

## Goals

- Run AnythingLLM locally.
- Configure one LLM provider.
- Configure embeddings.
- Confirm PDF/DOCX ingestion.
- Confirm RAG response and citations.

## Tasks

- add AnythingLLM to repo or as documented dependency
- create Docker Compose
- configure environment variables
- upload 3–5 documents
- test citations
- verify chat flow

## Definition of Done

- `docker compose up` works
- user can access UI
- PDF/DOCX upload works
- user can ask a question
- response contains usable citation/source

Do not customize UI heavily yet.

---

# Phase 2 — Demo Dataset
Estimated: 1 day

## Goals

Create realistic cross-source business data.

## Tasks

- generate Nova Retail documents
- generate Excel/CSV files
- create PostgreSQL schema
- create deterministic seed script
- document expected business story

## Definition of Done

At least five business questions have known expected answers.

Example:

- What is the VIP discount policy?
- Which product category lost the most Q3 revenue?
- Which SKUs have excessive inventory?
- Which VIP orders exceeded the allowed discount?
- Did marketing spend correlate with sales decline?

---

# Phase 3 — Intelligence Service Foundation
Estimated: 1 day

## Goals

Create independent FastAPI service.

## Initial endpoints

```text
GET  /health
POST /query
POST /data/upload
GET  /data/{dataset_id}/schema
POST /data/{dataset_id}/query
POST /database/test
POST /database/query
```

## Definition of Done

- service starts independently
- healthcheck passes
- request/response schemas defined
- logging exists
- unit test skeleton exists

---

# Phase 4 — Excel / CSV Data Engine
Estimated: 1–2 days

## Goals

Use DuckDB for spreadsheet and CSV analytics.

## Pipeline

```text
upload file
    ↓
detect file type
    ↓
register in DuckDB
    ↓
infer schema
    ↓
profile dataset
    ↓
query through controlled interface
```

## Required features

- XLSX
- CSV
- sheet detection
- row count
- column types
- null percentage
- distinct values
- min/max for numeric/date fields
- preview rows
- safe SQL execution

## API result example

```json
{
  "dataset_id": "sales_q3",
  "rows": 48213,
  "columns": [
    {"name": "date", "type": "DATE"},
    {"name": "product", "type": "VARCHAR"},
    {"name": "revenue", "type": "DOUBLE"}
  ]
}
```

---

# Phase 5 — PostgreSQL Read-Only Agent
Estimated: 1–2 days

## Goals

Allow natural-language analysis over business databases safely.

## Required security rules

The database user must be read-only.

Disallow:

- INSERT
- UPDATE
- DELETE
- DROP
- ALTER
- TRUNCATE
- CREATE
- GRANT
- REVOKE

Enforce:

- statement timeout
- row limit
- allowed schemas
- connection timeout
- result size limit

## SQL flow

```text
natural language
    ↓
schema context
    ↓
SQL generation
    ↓
SQL parser/validator
    ↓
optional EXPLAIN
    ↓
execute read-only
    ↓
structured result
```

## Result structure

```json
{
  "sql": "SELECT ...",
  "columns": [],
  "rows": [],
  "row_count": 42,
  "execution_ms": 31
}
```

The UI should support "View SQL".

---

# Phase 6 — Agent Router
Estimated: 1 day

## Goal

Determine which tool(s) are required.

Supported intents:

```text
knowledge
tabular
database
mixed
```

Examples:

- "What is the return policy?" → knowledge
- "What was Q3 revenue in sales.xlsx?" → tabular
- "How many VIP customers bought Product A?" → database
- "Did VIP discounts violate current policy?" → mixed

## Rule

Do not implement a large multi-agent architecture.

Use:

```text
one orchestrator
+
small explicit tools
```

This is easier to debug, evaluate, and deploy.

---

# Phase 7 — Cross-Source Reasoning
Estimated: 1 day

## Goal

Combine knowledge retrieval and structured data.

Required tools:

```text
search_knowledge()
query_file()
query_database()
```

## Main showcase query

> According to the current VIP discount policy, what was Q3 VIP revenue and how many orders exceeded the permitted discount?

Expected execution:

1. Retrieve sales policy.
2. Extract max allowed discount.
3. Query customer segment.
4. Query order discounts.
5. Calculate violations.
6. Generate explanation.
7. Attach citations.

## Definition of Done

The system successfully answers at least five mixed-source evaluation questions.

---

# Phase 8 — Data Explorer
Estimated: 1 day

## Goal

Show web/data engineering skill.

## Required screens

### Sources overview
Show:

- file name
- source type
- row/document count
- status
- last processed time

### Dataset detail
Tabs:

- Overview
- Schema
- Preview
- Profiling
- Query

### Database detail
Show:

- schemas
- tables
- estimated row counts
- columns
- data types

Avoid building a full BI platform.

---

# Phase 9 — Chart Generation
Estimated: 1 day

## Goal

Allow analytical responses to include validated chart specifications.

LLM should **not** generate arbitrary JavaScript/HTML.

Use a typed chart spec:

```json
{
  "type": "bar",
  "title": "Revenue by region",
  "x": "region",
  "y": "revenue"
}
```

Allowed chart types in V1:

- bar
- line
- pie/donut only if justified
- area
- simple table

Frontend renders the chart safely.

---

# Phase 10 — Evaluation Framework
Estimated: 2 days

This phase has very high portfolio value.

## Dataset format

Create 30–50 golden questions.

Example:

```json
{
  "question": "What is the VIP discount limit and how many Q3 orders exceeded it?",
  "expected_tools": ["knowledge", "database"],
  "expected_sources": ["sales-policy.pdf"],
  "expected_facts": ["12%"],
  "category": "mixed"
}
```

## Metrics

Track:

- tool selection accuracy
- SQL execution success
- answer correctness
- citation correctness
- source retrieval hit rate
- latency
- token usage
- estimated cost

## Important

Do not rely only on LLM-as-a-judge.

Where possible, use deterministic checks:

- SQL output equality/tolerance
- expected source ID
- expected numeric range
- expected tool selection

---

# Phase 11 — Query Inspector
Estimated: 1 day

## Goal

Make the system debuggable.

Display:

```text
User Question

Intent
→ mixed

Knowledge Tool
→ source list
→ scores

SQL Tool
→ generated SQL
→ execution time
→ row count

LLM
→ model
→ token usage
→ latency
```

This page is one of the strongest portfolio screenshots.

---

# Phase 12 — Observability
Estimated: 0.5–1 day

Use Langfuse Cloud initially.

Trace:

```text
request
 ├── router
 ├── knowledge search
 ├── file query
 ├── sql query
 └── response generation
```

Track:

- latency
- model
- tokens
- estimated cost
- failures
- tool duration

Do not self-host Langfuse in V1 unless there is a specific reason.

---

# Phase 13 — Deployment
Estimated: 1 day

## V1 production topology

```text
Internet
   ↓
Cloudflare
   ↓
Caddy / Nginx
   ↓
┌───────────────┬────────────────┐
│ AnythingLLM   │ FastAPI        │
└───────┬───────┴───────┬────────┘
        │               │
        │            DuckDB
        │
    PostgreSQL
```

Use Docker Compose.

## VPS target

Start with approximately:

- 2–4 vCPU
- 4–8 GB RAM

Use hosted LLM APIs.

Do not deploy a local production LLM in V1.

## Cost target

Aim for:

```text
VPS           $10–25/month
LLM API        $5–20/month
Domain         low
Langfuse       free initially
DuckDB         free
```

Expected total:

**~$15–45/month** for portfolio-level traffic.

---

# Phase 14 — CI/CD
Estimated: 0.5–1 day

## Pull request pipeline

- Python lint
- type checking where used
- unit tests
- integration tests
- frontend lint/build
- Docker build

## Main deployment

```text
merge to main
    ↓
build image
    ↓
push image
    ↓
deploy to VPS
    ↓
docker compose pull
    ↓
docker compose up -d
    ↓
healthcheck
```

Avoid Kubernetes.

---

# Phase 15 — Portfolio Packaging
Estimated: 1 day

## README structure

1. What the product does
2. 30-second GIF
3. Architecture diagram
4. Main showcase query
5. Evaluation results
6. Screenshots
7. What was reused vs custom built
8. Engineering tradeoffs
9. Local setup
10. Deployment

## Important README section

### What I built

Be explicit:

| Component | Source |
|---|---|
| Base chat UI | OSS |
| Document ingestion | OSS |
| Base RAG/citations | OSS |
| Agent router | Custom |
| DuckDB engine | Custom |
| PostgreSQL agent | Custom |
| SQL safety layer | Custom |
| Cross-source reasoning | Custom |
| Data Explorer | Custom |
| Chart spec engine | Custom |
| Evaluation framework | Custom |
| Query Inspector | Custom |
| CI/CD | Custom |

This prevents the portfolio from being mistaken for a simple rebrand/fork.

---

# 9. Priority Order

If schedule slips, prioritize in this order:

1. Cross-source reasoning
2. SQL/Data Agent
3. Evaluation
4. Data Explorer
5. Chart generation
6. Query Inspector
7. Observability
8. Extra integrations

Do not add Google Drive/Notion/Jira before evaluation quality is acceptable.

---

# 10. Quality Targets

V1 does not need perfect benchmark numbers, but it must be measurable.

Recommended initial goals:

```text
Tool selection accuracy     >= 90%
SQL execution success       >= 90%
Citation correctness        >= 85%
Mixed-source answer success >= 85%
P95 latency                 <= 8 sec for normal queries
```

These are engineering targets, not public claims unless verified.

---

# 11. Security Notes

## SQL

- read-only credentials
- validate SQL AST if possible
- enforce timeout
- enforce row limit
- deny DDL/DML
- restrict schemas

## Files

- validate extension and MIME type
- enforce size limits
- isolate upload paths
- sanitize filenames

## Secrets

Never commit:

- API keys
- database passwords
- Langfuse keys
- LLM credentials

Use `.env.example`.

## Logging

Never log:

- raw passwords
- connection strings with credentials
- API keys
- sensitive business rows unless explicitly required for debugging

---

# 12. Reliability Notes

## Tool execution

Each tool should return typed structured output.

Do not allow tools to return arbitrary text when structured output is possible.

## Retries

Retry:

- transient provider failures
- safe read-only HTTP/API calls

Do not blindly retry SQL or costly operations without constraints.

## Timeouts

Add explicit timeouts to:

- LLM calls
- database calls
- document ingestion
- external HTTP requests

---

# 13. AI Engineering Notes

## Avoid giant prompts

Separate:

- routing
- schema selection
- SQL generation
- answer synthesis

Do not place every document/schema/tool description into one prompt.

## Avoid unnecessary agents

Prefer:

```text
orchestrator
+ tools
```

over:

```text
planner agent
research agent
database agent
critic agent
review agent
manager agent
```

unless evaluation proves the complexity improves outcomes.

## Use deterministic logic where possible

Examples:

- SQL validation
- file detection
- schema extraction
- chart schema validation
- metric calculations

LLMs should reason, not replace deterministic software.

---

# 14. Data Engineering Notes

Excel should not be converted into RAG text by default.

Use:

```text
Excel/CSV
   ↓
DuckDB
   ↓
SQL / analytics
```

Documents use:

```text
PDF/DOCX
   ↓
parse
   ↓
chunk
   ↓
embed/index
```

Structured and unstructured data should remain separate until orchestration time.

---

# 15. Deployment Notes

V1 should run on one server.

Avoid premature:

- HA
- multi-region
- autoscaling
- service mesh
- managed Kubernetes

The goal is:

```text
git push
→ CI
→ Docker
→ VPS
```

A recruiter/client should be able to understand deployment in minutes.

---

# 16. Cost Optimization Notes

## Use hosted LLMs for low traffic

Portfolio traffic is low enough that API usage is usually cheaper than maintaining GPU infrastructure.

## Route models later

Optional V1.1:

- cheap model → classification/routing
- standard model → normal Q&A
- stronger model → difficult cross-source analysis

Do not introduce model routing before the core product works.

## Cache only measurable bottlenecks

Do not add Redis automatically.

Add caching when:

- repeated document retrieval is expensive
- repeated schema queries occur
- evaluation demonstrates a clear benefit

---

# 17. Testing Strategy

## Unit tests

Focus on:

- SQL validator
- schema extraction
- profiler
- chart validation
- router parsing
- typed tool outputs

## Integration tests

- DuckDB file queries
- PostgreSQL read-only queries
- AnythingLLM knowledge retrieval
- LLM mocked responses where appropriate

## Evaluation tests

Run golden questions against the full system.

## E2E

At minimum:

### Flow 1
Upload policy document → ask policy question → citation visible.

### Flow 2
Connect PostgreSQL → ask revenue question → inspect SQL.

### Flow 3
Ask mixed policy + revenue question → combined answer.

---

# 18. ADRs to Create

Create lightweight Architecture Decision Records:

```text
001-use-anythingllm-as-rag-shell.md
002-separate-fastapi-intelligence-service.md
003-use-duckdb-for-file-analytics.md
004-readonly-postgresql-agent.md
005-single-orchestrator-over-multi-agent.md
006-docker-compose-over-kubernetes.md
007-hosted-llm-over-local-gpu.md
008-evaluation-before-extra-connectors.md
```

Each ADR should contain:

- context
- decision
- alternatives
- consequences

---

# 19. V1 Exit Criteria

V1 is complete when all are true:

- Docker Compose starts the system.
- PDF/DOCX RAG works.
- Excel/CSV analysis works.
- PostgreSQL read-only analysis works.
- Router chooses correct source/tool.
- At least five cross-source questions work.
- Data Explorer exists.
- Charts render from typed specifications.
- Evaluation suite runs automatically.
- Query Inspector displays execution flow.
- Langfuse tracing exists.
- Public deployment exists.
- README explains custom vs reused code.
- Demo video/GIF exists.

Do not delay V1 for additional connectors.

---

# 20. Post-V1 Roadmap

## V1.1
- Website ingestion
- report export
- improved chart support
- model routing

## V1.2
- Google Drive
- Notion
- scheduled data refresh

## V2
- action tools
- human approval
- internal API calls
- role permissions

## V2.5
- stronger workspace isolation
- organization support

## V3
- multi-tenant SaaS
- billing
- commercial deployment modes

Only move into V2/V3 if the project has either:
- portfolio need
- real user demand
- commercial signal

---

# 21. Final Engineering Principle

The goal is **not** to build the largest AI platform.

The goal is to demonstrate:

> The developer can take an existing production OSS foundation, understand its boundaries, extend it with structured-data intelligence, build safe AI tooling, measure system quality, and deploy the full product economically.

Every engineering decision should support that goal.
