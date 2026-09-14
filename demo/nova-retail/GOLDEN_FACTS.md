# Nova Retail Golden Facts

This file is the deterministic source of truth for the Phase 2 dataset. Values are validated against the live PostgreSQL database by `validation/validate_dataset.py`.

## Dataset Counts

- Customer count: 5,000
- Product count: 120
- Order count: 50,000
- Payment count: 50,000
- Inventory record count: 120
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
