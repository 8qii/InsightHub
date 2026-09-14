# Phase 1.5 RAG Validation Report

Executed: yes

LLM provider: OpenAI-compatible `generic-openai`

Model used: `gpt-5.6-luna`

Embedding provider: AnythingLLM native embedder

Embedding model: `Xenova/all-MiniLM-L6-v2`

Vector storage: AnythingLLM-managed LanceDB

Workspace: `insighthub-demo`

Workspace similarity threshold: `0.15`

Documents:

- `sales_policy.md`
- `inventory_policy.md`
- `q3_business_review.md`

## Question 1

Question: `What is the maximum VIP discount allowed?`

Answer received: The maximum VIP discount allowed is 12% of the current list price. Discounts above 12% require commercial approval.

Citation received: yes, `sales_policy.md`

## Question 2

Question: `What happened to Product Luna in Q3?`

Answer received: Product Luna revenue declined by 18% in Q3 compared with the previous quarter, due to lower regional demand and extended replenishment lead times.

Citation received: yes, `q3_business_review.md`

No API keys, private documents, or generated runtime data are stored in this report.
