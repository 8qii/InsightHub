# InsightHub Demo Script

## Scenario

Nova Retail Distribution is a fictional distributor with business evidence split across policy documents, operational reviews, and PostgreSQL transaction data. The leadership team needs fast, defensible answers without manually reconciling separate systems.

The demo shows InsightHub selecting the smallest useful tool set, citing documents when policy matters, querying read-only business data for metrics, and exposing a sanitized execution trace.

## Preparation

1. Start the stack with `docker compose --env-file .env -f deployment/docker-compose.yml up -d --build`.
2. Open the analyst at `http://localhost:3000`.
3. Confirm the Nova Retail documents are indexed in the configured AnythingLLM workspace.
4. Keep the dashboard at `http://localhost:3000/dashboard` available in a second tab.

## Demo Flow

### 1. Policy Question

Ask:

> What is the maximum VIP discount allowed?

Expected answer:

- The maximum VIP discount is 12% of the current list price.
- Discounts above 12% require commercial approval.
- The response cites `sales_policy.md`.

What to point out:

- InsightHub uses document retrieval rather than treating a policy question as a database query.
- The answer includes a source citation for review.

### 2. Operational Analysis

Ask:

> Why did Product Luna revenue decline in Q3?

Expected answer:

- Product Luna revenue fell 18%, from $300,000 in Q2 to $246,000 in Q3.
- The Q3 business review identifies lower regional demand and extended replenishment lead times.
- The product had 12,000 units of inventory, aged 138 days as of September 30, 2025.
- The response cites `q3_business_review.md` and combines it with structured sales and inventory evidence.

What to point out:

- This is a mixed-source response: document evidence supplies business context while typed data tools provide numerical evidence.
- Expand the execution trace after the response to show tool names, durations, and status without exposing prompts or business rows.

### 3. Primary Showcase: Policy and Compliance

Ask:

> What is the maximum VIP discount, how much Q3 VIP revenue did we generate, and how many orders violated the policy?

Expected answer:

- The policy cap is 12%.
- Q3 VIP revenue is $3,137,371.50.
- There are 180 discount events above the policy limit; 120 are unapproved violations.
- The policy evidence is cited and the response explains that approved exceptions are tracked separately.

What to point out:

- One answer connects an unstructured policy rule with PostgreSQL-backed commercial metrics.
- The database access remains behind typed, read-only application tools rather than accepting arbitrary SQL from the browser.
- The streamed response and trace make the experience feel responsive and inspectable.

### 4. Executive View

Open the dashboard at `http://localhost:3000/dashboard`.

Expected view:

- Revenue, inventory risk, and discount-control KPIs.
- Lightweight charts for revenue trend and discount violations.

What to point out:

- The dashboard is intentionally focused on a few decision-relevant metrics, not a general BI platform.
- It uses the same backend data services as the analyst experience.

## Close

Summarize the product as a deliberately small, deployable knowledge and data analyst: RAG and citations for documents, read-only structured data tools for metrics, deterministic evaluation, and a traceable user experience.

## Troubleshooting

- If knowledge answers have no citations, verify the configured AnythingLLM workspace contains the Nova Retail documents.
- If the analyst cannot reach a model provider, verify the uncommitted `.env` values for `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`.
- If data answers fail, confirm `docker compose --env-file .env -f deployment/docker-compose.yml ps` reports healthy services.
