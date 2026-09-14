"""Validate the Nova Retail database against its golden facts."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
GOLDEN_PATH = ROOT / "demo" / "nova-retail" / "GOLDEN_FACTS.md"


def database_url() -> str:
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DATABASE", "nova_retail")
    user = os.getenv("POSTGRES_USER", "nova_retail")
    password = os.environ["POSTGRES_PASSWORD"]
    return f"host={host} port={port} dbname={database} user={user} password={password}"


def golden_values() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in GOLDEN_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^- ([^:]+): (.+)$", line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def money(value: Any) -> str:
    return f"${float(value):,.2f}"


def validate() -> None:
    facts = golden_values()
    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            assert cursor.fetchone()[0] == os.getenv("POSTGRES_DATABASE", "nova_retail")

            expected_counts = {
                "Customer count": ("customers", 5000),
                "Product count": ("products", 120),
                "Order count": ("orders", 50000),
                "Payment count": ("payments", 50000),
                "Inventory record count": ("inventory", 120),
                "Discount event count": ("discount_events", 1500),
            }
            for label, (table, expected) in expected_counts.items():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                actual = cursor.fetchone()[0]
                assert actual == expected == int(facts[label].replace(",", "")), (
                    f"{label}: {actual}"
                )

            cursor.execute("SELECT id FROM products WHERE name = 'Product Luna'")
            luna_id = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT COALESCE(SUM(o.amount), 0)
                FROM orders o
                WHERE o.product_id = %s
                  AND o.order_date >= DATE '2025-04-01'
                  AND o.order_date < DATE '2025-07-01'
                """,
                (luna_id,),
            )
            luna_q2 = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT COALESCE(SUM(o.amount), 0)
                FROM orders o
                WHERE o.product_id = %s
                  AND o.order_date >= DATE '2025-07-01'
                  AND o.order_date < DATE '2025-10-01'
                """,
                (luna_id,),
            )
            luna_q3 = cursor.fetchone()[0]
            decline = (float(luna_q2) - float(luna_q3)) / float(luna_q2) * 100
            assert money(luna_q2) == facts["Product Luna Q2 revenue"]
            assert money(luna_q3) == facts["Product Luna Q3 revenue"]
            assert round(decline, 2) == float(facts["Product Luna Q3 decline"].rstrip("%"))
            assert decline > 0

            cursor.execute(
                """
                SELECT COALESCE(SUM(o.amount), 0)
                FROM orders o
                JOIN customers c ON c.id = o.customer_id
                WHERE c.segment = 'VIP'
                  AND o.order_date >= DATE '2025-07-01'
                  AND o.order_date < DATE '2025-10-01'
                """
            )
            assert money(cursor.fetchone()[0]) == facts["VIP revenue Q3"]

            cursor.execute(
                "SELECT MAX(discount_percent), COUNT(*) "
                "FROM discount_events WHERE discount_percent > 12"
            )
            maximum_discount, above_limit = cursor.fetchone()
            assert f"{float(maximum_discount):.0f}%" == facts["Maximum observed discount"]
            assert above_limit == int(facts["Discount events above policy limit"])

            cursor.execute(
                "SELECT COUNT(*) FROM discount_events "
                "WHERE discount_percent > 12 AND approved = false"
            )
            assert cursor.fetchone()[0] == int(facts["Unapproved discount violations"])

            cursor.execute(
                """
                SELECT i.stock_quantity, DATE '2025-09-30' - i.updated_at::date
                FROM inventory i WHERE i.product_id = %s
                """,
                (luna_id,),
            )
            stock_quantity, age = cursor.fetchone()
            assert stock_quantity == int(facts["Product Luna inventory quantity"].replace(",", ""))
            assert age >= 90
            assert age == int(facts["Product Luna inventory age"].split()[0])

    print(
        "Nova Retail dataset validation passed: schema, counts, golden facts, Luna revenue, "
        "and discount compliance."
    )


if __name__ == "__main__":
    validate()
