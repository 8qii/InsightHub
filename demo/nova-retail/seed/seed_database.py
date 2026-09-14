"""Seed the deterministic Nova Retail PostgreSQL demonstration database."""

from __future__ import annotations

import os
import random
from datetime import UTC, date, datetime, timedelta
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
WAREHOUSES = ("East Hub", "Central Hub", "West Hub")
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
    products = [(1, "Product Luna", CATEGORIES[0], 100.00)]
    for product_id in range(2, 121):
        category = CATEGORIES[(product_id - 2) % len(CATEGORIES)]
        price = round(25 + ((product_id * 37) % 275) + (product_id % 4) * 0.25, 2)
        products.append((product_id, f"Nova {category} {product_id:03d}", category, price))
    return products


def make_orders(products: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    prices = {row[0]: row[3] for row in products}
    orders: list[tuple[Any, ...]] = []
    order_id = 1

    # Fixed Luna volumes make the documented Q2 to Q3 decline exactly 18%.
    for quarter_start, count in ((date(2025, 4, 1), 3000), (date(2025, 7, 1), 2460)):
        for index in range(count):
            order_date = quarter_start + timedelta(days=index % 91)
            customer_id = ((index * 17 + (0 if count == 3000 else 11)) % 5000) + 1
            orders.append((order_id, customer_id, 1, 1, 100.00, order_date))
            order_id += 1

    for index in range(50000 - len(orders)):
        product_id = 2 + (index * 29) % 119
        quantity = 1 + (index % 4)
        order_date = date(2025, 4, 1) + timedelta(days=(index * 7) % 183)
        customer_id = ((index * 31 + 97) % 5000) + 1
        amount = round(float(prices[product_id]) * quantity, 2)
        orders.append((order_id, customer_id, product_id, quantity, amount, order_date))
        order_id += 1
    return orders


def make_payments(orders: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    return [
        (
            order[0],
            order[0],
            "paid" if order[0] % 23 else "pending",
            order[4],
        )
        for order in orders
    ]


def make_inventory(products: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for product_id, *_ in products:
        if product_id == 1:
            quantity = 12000
            updated_at = datetime(2025, 5, 15, tzinfo=UTC)
        else:
            quantity = 180 + ((product_id * 43) % 420)
            updated_at = datetime(2025, 9, 1, tzinfo=UTC) + timedelta(days=product_id % 20)
        rows.append(
            (product_id, product_id, quantity, WAREHOUSES[(product_id - 1) % 3], updated_at)
        )
    return rows


def make_discount_events(orders: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    events: list[tuple[Any, ...]] = []
    rng = random.Random(SEED)
    selected_orders = rng.sample(orders, 1500)
    for event_id, order in enumerate(selected_orders, start=1):
        if event_id <= 120:
            discount = 15 + (event_id % 11)
            approved = False
        elif event_id <= 180:
            discount = 13 + (event_id % 8)
            approved = True
        else:
            discount = 5 + (event_id % 8)
            approved = True
        events.append(
            (
                event_id,
                order[0],
                float(discount),
                approved,
                datetime.combine(order[5], datetime.min.time(), UTC),
            )
        )
    return events


def seed() -> None:
    customers = make_customers()
    products = make_products()
    orders = make_orders(products)
    payments = make_payments(orders)
    inventory = make_inventory(products)
    discount_events = make_discount_events(orders)

    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DROP TABLE IF EXISTS discount_events, inventory, payments, orders, products, "
                "customers CASCADE"
            )
            cursor.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
        with connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO customers (id, name, segment, region, created_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                customers,
            )
            cursor.executemany(
                "INSERT INTO products (id, name, category, price) VALUES (%s, %s, %s, %s)",
                products,
            )
            cursor.executemany(
                "INSERT INTO orders (id, customer_id, product_id, quantity, amount, order_date) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                orders,
            )
            cursor.executemany(
                "INSERT INTO payments (id, order_id, payment_status, amount) "
                "VALUES (%s, %s, %s, %s)",
                payments,
            )
            cursor.executemany(
                "INSERT INTO inventory (id, product_id, stock_quantity, warehouse, updated_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                inventory,
            )
            cursor.executemany(
                "INSERT INTO discount_events (id, order_id, discount_percent, approved, "
                "created_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                discount_events,
            )
    print(
        "Seeded Nova Retail: 5000 customers, 120 products, 50000 orders, 50000 payments, "
        "120 inventory rows, 1500 discount events."
    )


if __name__ == "__main__":
    seed()
