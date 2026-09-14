# Nova Retail Discount Policy

## VIP Discount Limit

VIP customers have a maximum standard discount of **12%**.

Discounts above 12% require manager approval before the order is finalized. An approved exception may exceed the standard limit, but the exception must remain recorded in `discount_events`.

## Compliance Review

An order is a discount violation when its discount event has `discount_percent > 12` and `approved = false`. Compliance reporting should count violating discount events, not simply all discounts above 12%, because approved exceptions are permitted.

The discount operations team reviews violations weekly and escalates repeated exceptions by region and customer segment.
