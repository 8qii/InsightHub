"""Seed the deterministic Nova Retail PostgreSQL operational dataset."""

from __future__ import annotations

import os
import random
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
SCHEMA_PATH = ROOT / "demo" / "nova-retail" / "database" / "schema.sql"
SEED = 20250930
AS_OF = date(2025, 9, 30)
REGIONS = ("Northeast", "Southeast", "Midwest", "West")
WAREHOUSES = ((1, "East Hub", "Northeast"), (2, "Central Hub", "Midwest"), (3, "West Hub", "West"))
CHANNELS = ("Web", "Mobile", "Marketplace")
CATEGORIES = ("Consumer Electronics", "Home Goods", "Apparel", "Accessories")


def database_url() -> str:
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DATABASE", "nova_retail")
    user = os.getenv("POSTGRES_USER", "nova_retail")
    password = os.environ["POSTGRES_PASSWORD"]
    return f"host={host} port={port} dbname={database} user={user} password={password}"


def make_customers() -> list[tuple[Any, ...]]:
    segments = ("VIP", "Premium", "Standard")
    return [
        (
            customer_id,
            f"Nova Customer {customer_id:05d}",
            segments[(customer_id - 1) % len(segments)],
            REGIONS[(customer_id - 1) % len(REGIONS)],
            datetime(2022, 1, 1, tzinfo=UTC) + timedelta(days=customer_id % 1300),
        )
        for customer_id in range(1, 5001)
    ]


def make_products() -> list[tuple[Any, ...]]:
    products = [(1, "Product Luna", CATEGORIES[0], Decimal("100.00"), Decimal("58.00"))]
    for product_id in range(2, 121):
        category = CATEGORIES[(product_id - 2) % len(CATEGORIES)]
        price = Decimal(str(round(25 + ((product_id * 37) % 275) + (product_id % 4) * 0.25, 2)))
        cost = (price * Decimal("0.61")).quantize(Decimal("0.01"))
        products.append((product_id, f"Nova {category} {product_id:03d}", category, price, cost))
    return products


def make_orders(products: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    prices = {row[0]: row[3] for row in products}
    orders: list[tuple[Any, ...]] = []
    order_id = 1

    # Fixed Luna volumes preserve the documented $300,000 Q2 / $246,000 Q3 revenue truth.
    for quarter_start, count in ((date(2025, 4, 1), 3000), (date(2025, 7, 1), 2460)):
        for index in range(count):
            order_date = quarter_start + timedelta(days=index % 91)
            customer_id = ((index * 17 + (0 if count == 3000 else 11)) % 5000) + 1
            region = REGIONS[(customer_id - 1) % len(REGIONS)]
            orders.append((order_id, customer_id, 1, 1, prices[1], order_date, region, CHANNELS[index % 3]))
            order_id += 1

    for index in range(50000 - len(orders)):
        product_id = 2 + (index * 29) % 119
        quantity = 1 + (index % 4)
        order_date = date(2025, 4, 1) + timedelta(days=(index * 7) % 183)
        customer_id = ((index * 31 + 97) % 5000) + 1
        region = REGIONS[(customer_id - 1) % len(REGIONS)]
        orders.append(
            (order_id, customer_id, product_id, quantity, prices[product_id] * quantity, order_date, region, CHANNELS[index % 3])
        )
        order_id += 1
    return orders


def make_order_items(
    orders: list[tuple[Any, ...]], products: list[tuple[Any, ...]]
) -> tuple[list[tuple[Any, ...]], dict[int, Decimal]]:
    prices = {row[0]: row[3] for row in products}
    costs = {row[0]: row[4] for row in products}
    items: list[tuple[Any, ...]] = []
    totals: dict[int, Decimal] = {}
    item_id = 1
    for order in orders:
        order_id, customer_id, product_id, quantity, _, order_date, _, _ = order
        gross = prices[product_id] * quantity
        items.append((item_id, order_id, product_id, quantity, prices[product_id], Decimal("0.00"), costs[product_id] * quantity))
        totals[order_id] = gross
        item_id += 1
        # Add a second item to 40% of orders, excluding VIP Q3 and Luna orders so
        # existing documented revenue facts continue to refer to their same population.
        is_vip_q3 = customer_id % 3 == 1 and order_date >= date(2025, 7, 1)
        if product_id != 1 and order_id % 5 in (0, 1) and not is_vip_q3:
            extra_product_id = 2 + ((product_id * 13 + order_id) % 119)
            extra_quantity = 1 + (order_id % 2)
            extra_gross = prices[extra_product_id] * extra_quantity
            discount = (extra_gross * Decimal("0.05")).quantize(Decimal("0.01")) if order_id % 10 == 0 else Decimal("0.00")
            items.append((item_id, order_id, extra_product_id, extra_quantity, prices[extra_product_id], discount, costs[extra_product_id] * extra_quantity))
            totals[order_id] += extra_gross
            item_id += 1
    return items, totals


def make_payments(orders: list[tuple[Any, ...]], totals: dict[int, Decimal]) -> list[tuple[Any, ...]]:
    return [(order[0], order[0], "paid" if order[0] % 23 else "pending", totals[order[0]]) for order in orders]


def make_returns(
    items: list[tuple[Any, ...]], orders: list[tuple[Any, ...]]
) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    reasons = ("Damaged", "Changed mind", "Incorrect item", "Quality concern")
    order_dates = {order[0]: order[5] for order in orders}
    for item in items:
        item_id, order_id, product_id, quantity, unit_price, discount, _, = item
        # Product Luna has a deliberately richer but non-narrative-specific return sample.
        selected = item_id % 11 == 0 or (product_id == 1 and item_id % 7 == 0)
        if not selected:
            continue
        returned_quantity = quantity if item_id % 4 else 1
        net_unit_price = (unit_price - (discount / quantity)).quantize(Decimal("0.01"))
        rows.append(
            (
                len(rows) + 1,
                order_id,
                item_id,
                returned_quantity,
                order_dates[order_id] + timedelta(days=5 + item_id % 45),
                reasons[item_id % len(reasons)],
                net_unit_price * returned_quantity,
            )
        )
    return rows


def make_inventory(products: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    return [
        (product_id, product_id, 12000 if product_id == 1 else 540 + ((product_id * 43) % 1260), "Central Hub" if product_id == 1 else WAREHOUSES[(product_id - 1) % 3][1], datetime(2025, 10, 31, tzinfo=UTC))
        for product_id, *_ in products
    ]


def make_inventory_snapshots(products: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    snapshot_dates = (date(2025, 6, 30), AS_OF, date(2025, 10, 31))
    for snapshot_date in snapshot_dates:
        for product_id, *_ in products:
            for warehouse_id, _, _ in WAREHOUSES:
                if product_id == 1 and snapshot_date == AS_OF:
                    on_hand = 12000 if warehouse_id == 2 else 0
                    reserved = 900 if warehouse_id == 2 else 0
                    received_at = date(2025, 5, 15)
                else:
                    on_hand = 180 + ((product_id * 43 + warehouse_id * 71 + snapshot_date.month * 29) % 420)
                    reserved = (product_id * warehouse_id + snapshot_date.month) % min(60, on_hand + 1)
                    received_at = snapshot_date - timedelta(days=20 + ((product_id * 11 + warehouse_id * 17) % 160))
                rows.append((len(rows) + 1, product_id, warehouse_id, snapshot_date, on_hand, reserved, received_at))
    return rows


def make_discount_events(orders: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    events: list[tuple[Any, ...]] = []
    rng = random.Random(SEED)
    selected_orders = rng.sample(orders, 1500)
    for event_id, order in enumerate(selected_orders, start=1):
        if event_id <= 120:
            discount, approved = 15 + (event_id % 11), False
        elif event_id <= 180:
            discount, approved = 13 + (event_id % 8), True
        else:
            discount, approved = 5 + (event_id % 8), True
        events.append((event_id, order[0], Decimal(discount), approved, datetime.combine(order[5], datetime.min.time(), UTC)))
    return events


def seed() -> None:
    customers = make_customers()
    products = make_products()
    orders = make_orders(products)
    order_items, totals = make_order_items(orders, products)
    orders = [(*order[:4], totals[order[0]], *order[5:]) for order in orders]
    payments = make_payments(orders, totals)
    returns = make_returns(order_items, orders)
    inventory = make_inventory(products)
    snapshots = make_inventory_snapshots(products)
    discount_events = make_discount_events(orders)

    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS discount_events, returns, inventory_snapshots, inventory, payments, order_items, orders, warehouses, products, customers CASCADE")
            cursor.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
            cursor.executemany("INSERT INTO customers (id, name, segment, region, created_at) VALUES (%s, %s, %s, %s, %s)", customers)
            cursor.executemany("INSERT INTO products (id, name, category, price, unit_cost) VALUES (%s, %s, %s, %s, %s)", products)
            cursor.executemany("INSERT INTO warehouses (id, name, region) VALUES (%s, %s, %s)", WAREHOUSES)
            cursor.executemany("INSERT INTO orders (id, customer_id, product_id, quantity, amount, order_date, region, sales_channel) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", orders)
            cursor.executemany("INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, discount_amount, cost_basis) VALUES (%s, %s, %s, %s, %s, %s, %s)", order_items)
            cursor.executemany("INSERT INTO returns (id, order_id, order_item_id, returned_quantity, return_date, reason, refund_amount) VALUES (%s, %s, %s, %s, %s, %s, %s)", returns)
            cursor.executemany("INSERT INTO payments (id, order_id, payment_status, amount) VALUES (%s, %s, %s, %s)", payments)
            cursor.executemany("INSERT INTO inventory (id, product_id, stock_quantity, warehouse, updated_at) VALUES (%s, %s, %s, %s, %s)", inventory)
            cursor.executemany("INSERT INTO inventory_snapshots (id, product_id, warehouse_id, snapshot_date, on_hand_quantity, reserved_quantity, received_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", snapshots)
            cursor.executemany("INSERT INTO discount_events (id, order_id, discount_percent, approved, created_at) VALUES (%s, %s, %s, %s, %s)", discount_events)
    print(f"Seeded Nova Retail: {len(customers)} customers, {len(products)} products, {len(orders)} orders, {len(order_items)} order items, {len(returns)} returns, {len(snapshots)} inventory snapshots.")


if __name__ == "__main__":
    seed()
