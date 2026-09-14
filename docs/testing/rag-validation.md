# Phase 1.5 RAG Validation

This procedure validates the real AnythingLLM path with real model inference, real embeddings, real documents, and citation output. It does not create a custom vector store or embedding pipeline.

## Setup

1. Copy `.env.example` to `.env` without committing the copy.
2. Start the services:

   ```bash
   docker compose -f deployment/docker-compose.yml up -d
   ```

3. Open `http://localhost:3001` and complete AnythingLLM's initial setup.
4. Configure the LLM provider as OpenAI Compatible (`generic-openai`):
   - Base URL: `http://host.docker.internal:8317/v1`
   - Model: `gpt-5.6-luna`
   - API key: configure locally and do not record it in this repository.
5. Configure the embedding provider and model in AnythingLLM. The reproducible default is the managed native embedder with `Xenova/all-MiniLM-L6-v2`. Record the actual selection in the validation report; do not substitute the chat model unless the provider explicitly supports embeddings.
6. Create a workspace named `insighthub-demo`.
   - For the native `Xenova/all-MiniLM-L6-v2` embedder, use a similarity threshold of `0.15` or lower for this small demo corpus. The default `0.7` threshold can reject semantically relevant short-document matches.
7. Upload these documents from `demo/company/`:
   - `sales_policy.md`
   - `inventory_policy.md`
   - `q3_business_review.md`
8. Wait for ingestion and embedding to complete.
9. Create an AnythingLLM Developer API key and set it only in the local `.env` as `ANYTHINGLLM_API_KEY`.
10. Restart the Intelligence service if the environment file was changed.

## Test Question 1

Question:

```text
What is the maximum VIP discount allowed?
```

Expected answer: `12%`.

Expected source: `sales_policy.md`.

Call the InsightHub API:

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/query \
  -H 'Content-Type: application/json' \
  -d '{"workspace_id":"insighthub-demo","query":"What is the maximum VIP discount allowed?"}'
```

Record the returned answer and at least one normalized citation whose title or URI identifies `sales_policy.md`.

## Test Question 2

Question:

```text
What happened to Product Luna in Q3?
```

Expected answer: `Revenue declined by 18%`.

Expected source: `q3_business_review.md`.

Record the returned answer and at least one normalized citation whose title or URI identifies `q3_business_review.md`.

## Validation Report

Keep the report free of keys and private document contents. Record only:

```text
model used:
embedding used:
workspace: insighthub-demo
question:
answer received:
citation received: yes/no
```
