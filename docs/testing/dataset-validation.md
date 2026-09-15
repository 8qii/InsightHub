# Nova Retail Dataset Validation

## Prerequisites

Start PostgreSQL from the repository root:

```bash
docker compose --env-file .env -f deployment/docker-compose.yml up -d postgres
```

Install the seed dependency in a local Python 3.12 environment:

```bash
python -m pip install -r demo/nova-retail/seed/requirements.txt
```

## Seed

The seed script uses `POSTGRES_*` variables from `.env`. It drops and recreates the demo schema before inserting deterministic data, so rerunning it does not create uncontrolled duplicates.

```bash
python demo/nova-retail/seed/seed_database.py
```

## Validate

```bash
python demo/nova-retail/validation/validate_dataset.py
```

Validation checks target identity, row counts, return-to-item integrity, temporal validity, gross/post-discount/net revenue, returns, margin, Product Luna Q2/Q3 revenue, VIP Q3 revenue, regional/channel performance, and the 2025-09-30 Product Luna Central Hub snapshot. It queries a live PostgreSQL instance and fails on any deterministic mismatch.
