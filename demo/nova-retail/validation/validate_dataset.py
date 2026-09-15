"""Validate the Nova Retail operational dataset against deterministic golden facts."""

from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
GOLDEN_PATH = ROOT / "demo" / "nova-retail" / "GOLDEN_FACTS.md"
AS_OF = "2025-09-30"


def database_url() -> str:
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DATABASE", "nova_retail")
    user = os.getenv("POSTGRES_USER", "nova_retail")
    password = os.environ["POSTGRES_PASSWORD"]
    return f"host={host} port={port} dbname={database} user={user} password={password}"


def scalar(cursor: psycopg.Cursor[object], query: str, params: tuple[object, ...] = ()) -> object:
    cursor.execute(query, params)
    return cursor.fetchone()[0]


def validate() -> None:
    golden_facts = GOLDEN_PATH.read_text(encoding="utf-8")
    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            assert scalar(cursor, "SELECT current_database()") == os.getenv(
                "POSTGRES_DATABASE", "nova_retail"
            )

            expected_counts = {
                "customers": 5000,
                "products": 120,
                "orders": 50000,
                "order_items": 64837,
                "returns": 6604,
                "payments": 50000,
                "inventory": 120,
                "warehouses": 3,
                "inventory_snapshots": 1080,
                "discount_events": 1500,
            }
            for table, expected in expected_counts.items():
                actual = scalar(cursor, f"SELECT COUNT(*) FROM {table}")
                assert actual == expected, f"{table}: {actual} != {expected}"

            assert scalar(
                cursor,
                """
                SELECT COUNT(*) FROM returns r
                LEFT JOIN order_items oi ON oi.id = r.order_item_id AND oi.order_id = r.order_id
                WHERE oi.id IS NULL OR r.returned_quantity > oi.quantity
                """,
            ) == 0
            assert scalar(
                cursor,
                """
                SELECT COUNT(*) FROM returns r JOIN orders o ON o.id = r.order_id
                WHERE r.return_date < o.order_date
                """,
            ) == 0

            cursor.execute(
                """
                SELECT SUM(oi.quantity * oi.unit_price),
                       SUM(oi.quantity * oi.unit_price - oi.discount_amount),
                       SUM(oi.quantity),
                       COUNT(DISTINCT o.id),
                       SUM(oi.quantity * oi.unit_price - oi.discount_amount - oi.cost_basis)
                FROM order_items oi JOIN orders o ON o.id = oi.order_id
                """
            )
            gross_revenue, post_discount_revenue, units_sold, order_count, margin_before_returns = cursor.fetchone()
            refunds = scalar(cursor, "SELECT SUM(refund_amount) FROM returns")
            assert gross_revenue == Decimal("22309873.25")
            assert post_discount_revenue == Decimal("22280028.28")
            assert refunds == Decimal("1813781.08")
            assert units_sold == 139072
            assert order_count == 50000
            assert post_discount_revenue - refunds == Decimal("20466247.20")
            assert margin_before_returns == Decimal("8687357.12")
            assert margin_before_returns - refunds == Decimal("6873576.04")

            cursor.execute(
                """
                SELECT SUM(oi.quantity * oi.unit_price - oi.discount_amount)
                FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
                JOIN customers c ON c.id = o.customer_id
                WHERE c.segment = 'VIP'
                  AND o.order_date >= DATE '2025-07-01' AND o.order_date < DATE '2025-10-01'
                """
            )
            assert cursor.fetchone()[0] == Decimal("3137371.50")

            cursor.execute(
                "SELECT MAX(discount_percent), COUNT(*) FROM discount_events WHERE discount_percent > 12"
            )
            assert cursor.fetchone() == (Decimal("25.00"), 180)
            assert scalar(
                cursor,
                "SELECT COUNT(*) FROM discount_events WHERE discount_percent > 12 AND approved = false",
            ) == 120

            cursor.execute(
                """
                SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
                JOIN products p ON p.id = oi.product_id
                WHERE p.name = 'Product Luna'
                  AND o.order_date >= DATE '2025-04-01' AND o.order_date < DATE '2025-07-01'
                """
            )
            assert cursor.fetchone()[0] == Decimal("300000.00")
            cursor.execute(
                """
                SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
                JOIN products p ON p.id = oi.product_id
                WHERE p.name = 'Product Luna'
                  AND o.order_date >= DATE '2025-07-01' AND o.order_date < DATE '2025-10-01'
                """
            )
            assert cursor.fetchone()[0] == Decimal("246000.00")

            cursor.execute(
                """
                SELECT o.region, o.sales_channel, SUM(oi.quantity * oi.unit_price - oi.discount_amount)
                FROM order_items oi JOIN orders o ON o.id = oi.order_id
                GROUP BY o.region, o.sales_channel ORDER BY 3 DESC LIMIT 1
                """
            )
            assert cursor.fetchone() == ("Midwest", "Web", Decimal("2665140.78"))

            cursor.execute(
                """
                SELECT s.on_hand_quantity, s.reserved_quantity, DATE '2025-09-30' - s.received_at
                FROM inventory_snapshots s
                JOIN products p ON p.id = s.product_id
                JOIN warehouses w ON w.id = s.warehouse_id
                WHERE p.name = 'Product Luna' AND w.name = 'Central Hub'
                  AND s.snapshot_date = DATE '2025-09-30'
                """
            )
            assert cursor.fetchone() == (12000, 900, 138)

            assert "Product Luna inventory quantity: 12,000" in golden_facts
            assert "Product Luna inventory age: 138 days as of 2025-09-30" in golden_facts

    print(
        "Nova Retail validation passed: row counts, FK integrity, sales, returns, margin, "
        "regional/channel performance, and historical Luna inventory."
    )


if __name__ == "__main__":
    validate()
