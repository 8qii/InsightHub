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
- Inventory: return products whose inventory update is older than a requested threshold.
- Discount: count events above a requested maximum and the subset that is unapproved.

The endpoints under `/api/v1/data/` are internal validation endpoints, not agent APIs. A future agent adapter can call the service layer or a dedicated typed tool boundary without changing repository code.

## Lifecycle and Configuration

`Database` creates an async SQLAlchemy engine using `postgresql+asyncpg`, exposes an async session factory, and disposes the engine during FastAPI shutdown. The schema remains owned by `demo/nova-retail/database/schema.sql`; this phase intentionally adds no migration system.
