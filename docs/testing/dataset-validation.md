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

The seed script uses `POSTGRES_*` variables from `.env`. It drops and recreates the six demo tables before inserting deterministic data, so rerunning it does not create uncontrolled duplicates.

```bash
python demo/nova-retail/seed/seed_database.py
```

## Validate

```bash
python demo/nova-retail/validation/validate_dataset.py
```

Validation checks that the target database and tables exist, record counts match, Product Luna revenue declines by 18%, VIP Q3 revenue matches the golden facts, discount violations are counted correctly, and Product Luna inventory requires review.
