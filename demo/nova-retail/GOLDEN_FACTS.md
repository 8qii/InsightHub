# Nova Retail Golden Facts

This file is the deterministic source of truth for the Nova Retail operational dataset. Values are validated against the live PostgreSQL database by `validation/validate_dataset.py`.

## Dataset Counts

- Customer count: 5,000
- Product count: 120
- Order count: 50,000
- Order item count: 64,837
- Return count: 6,604
- Payment count: 50,000
- Inventory record count: 120
- Warehouse count: 3
- Inventory snapshot count: 1,080
- Discount event count: 1,500

## Business Facts

- VIP revenue Q3: $3,137,371.50
- Policy maximum discount: 12%
- Maximum observed discount: 25%
- Discount events above policy limit: 180
- Unapproved discount violations: 120
- Product Luna Q2 revenue: $300,000.00
- Product Luna Q3 revenue: $246,000.00
- Product Luna Q3 decline: 18.00%
- Product Luna inventory quantity: 12,000
- Product Luna inventory review required: yes
- Product Luna inventory age: 138 days as of 2025-09-30

## Operational Metrics

- Gross revenue (Q2-Q3 2025): $22,309,873.25
- Post-discount revenue (Q2-Q3 2025): $22,280,028.28
- Net revenue after refunds (Q2-Q3 2025): $20,466,247.20
- Units sold (Q2-Q3 2025): 139,072
- Gross margin before refunds (Q2-Q3 2025): $8,687,357.12
- Gross margin after refunds (Q2-Q3 2025): $6,873,576.04
- Returned units (Q2-Q3 2025): 11,691
- Refund amount (Q2-Q3 2025): $1,813,781.08
- Return rate (Q2-Q3 2025): 8.4064%
- Product Luna return records: 1,206
- Product Luna returned units: 1,206
- Product Luna refunds: $120,600.00

## Dimensional and Inventory Facts

- Top region/channel by post-discount revenue (Q2-Q3 2025): Midwest / Web, $2,665,140.78
- Product Luna Central Hub on-hand quantity as of 2025-09-30: 12,000
- Product Luna Central Hub reserved quantity as of 2025-09-30: 900
- Product Luna Central Hub available quantity as of 2025-09-30: 11,100
- Product Luna Central Hub inventory age as of 2025-09-30: 138 days
