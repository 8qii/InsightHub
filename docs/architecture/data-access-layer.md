# Enterprise Data Access Layer

## Purpose

Phase 3 exposes Nova Retail business capabilities through typed service boundaries. Future agents will call these capabilities instead of receiving database credentials or constructing SQL. This keeps database access deterministic, auditable, and independently testable.

## Architecture

```text
Internal API / Future Agent Tool
              |
           Service
              |
         Repository
              |
       Async SQLAlchemy
              |
          PostgreSQL
```

The API validates business inputs such as quarter, age threshold, and maximum discount. Services own business behavior and safe error translation. Repositories own SQLAlchemy statements and database-specific query details. SQL never comes from a request body or query parameter.

## Capabilities

- Sales: summarize a named product for a 2025 calendar quarter.
- Inventory: return products whose inventory update is older than a requested threshold, optionally evaluated at a historical `as_of_date`.
- Discount: count events above a requested maximum and the subset that is unapproved.

The endpoints under `/api/v1/data/` are internal validation endpoints, not agent APIs. A future agent adapter can call the service layer or a dedicated typed tool boundary without changing repository code.

## Temporal and Snapshot Queries

Inventory age is calculated as `as_of_date - inventory.updated_at`. When `as_of_date` is omitted, the repository uses the current database date. Historical questions must provide the business snapshot date rather than relying on the runtime clock. For the Nova Retail Q3 business review, the snapshot date is `2025-09-30`; Product Luna is therefore 138 days old. Using the current date produces 487 days and can make a current operational fact look like a historical business cause.

The inventory API accepts `as_of_date=YYYY-MM-DD`, and the agent tool exposes the same optional field. This keeps snapshot analysis deterministic while preserving current-date behavior for operational queries.

## Lifecycle and Configuration

`Database` creates an async SQLAlchemy engine using `postgresql+asyncpg`, exposes an async session factory, and disposes the engine during FastAPI shutdown. The schema remains owned by `demo/nova-retail/database/schema.sql`; this phase intentionally adds no migration system.
