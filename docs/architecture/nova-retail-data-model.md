# Nova Retail Data Model

## Business Scenario

Nova Retail is a fictional e-commerce retailer with sales, customer segmentation, product catalog, fulfillment inventory, payments, and discount governance. The dataset covers Q2 and Q3 2025 so future data agents can compare a stable baseline with the Product Luna decline described in the business review.

## Entities and Relationships

| Entity | Purpose | Relationships |
| --- | --- | --- |
| `customers` | Customer identity, segment, and region | One customer has many orders |
| `products` | Catalog item, category, and price | One product has many orders and inventory records |
| `orders` | Revenue-bearing sales transactions | References one customer and one product |
| `payments` | Settlement state for an order | One-to-one with orders |
| `inventory` | Warehouse stock snapshot | References one product |
| `discount_events` | Discount requests and approval audit | References one order |

## Why Each Source Exists

The PostgreSQL tables represent operational data that should be queried relationally: revenue, customer segments, payments, inventory age, and discount compliance all depend on joins and aggregation. The Markdown documents represent policy and narrative knowledge: the 12% VIP discount limit, the 90-day inventory review rule, and the Q3 business interpretation. Keeping these sources separate creates a realistic foundation for future cross-source reasoning without building an agent in this phase.

The seed intentionally creates 5,000 customers, 120 products, 50,000 orders, 50,000 payments, 120 inventory records, and 1,500 discount events. Product Luna has exactly $300,000.00 in Q2 revenue and $246,000.00 in Q3 revenue, an 18% decline, plus 12,000 units of stale inventory.
