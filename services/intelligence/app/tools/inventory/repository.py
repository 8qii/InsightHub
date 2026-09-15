from datetime import date, timedelta

from sqlalchemy import Date, cast, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models import Inventory, InventorySnapshot, Product, Warehouse


class InventoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_risk(
        self, age_threshold_days: int, as_of_date: date | None = None
    ) -> list[tuple[str, int, int]]:
        if as_of_date is not None:
            age_days = (literal(as_of_date) - InventorySnapshot.received_at).label("age_days")
            statement = (
                select(
                    Product.name,
                    func.sum(InventorySnapshot.on_hand_quantity).label("stock_quantity"),
                    func.max(age_days).label("age_days"),
                )
                .join(InventorySnapshot, InventorySnapshot.product_id == Product.id)
                .where(InventorySnapshot.snapshot_date == as_of_date)
                .group_by(Product.name)
                .having(func.max(age_days) >= age_threshold_days)
                .order_by(func.max(age_days).desc(), Product.name)
            )
            rows = (await self.session.execute(statement)).all()
            return [(row.name, int(row.stock_quantity), int(row.age_days)) for row in rows]

        effective_date = func.current_date()
        age_days = (effective_date - cast(Inventory.updated_at, Date)).label("age_days")
        cutoff = (as_of_date or date.today()) - timedelta(days=age_threshold_days)
        statement = (
            select(Product.name, Inventory.stock_quantity, age_days)
            .join(Inventory, Inventory.product_id == Product.id)
            .where(Inventory.updated_at < cutoff)
            .order_by(age_days.desc(), Product.name)
        )
        rows = (await self.session.execute(statement)).all()
        return [(row.name, int(row.stock_quantity), int(row.age_days)) for row in rows]

    async def get_snapshot(
        self, product_name: str | None, warehouse_name: str | None, snapshot_date: date
    ) -> list[tuple[str, str, date, int, int, int, int]]:
        age_days = (literal(snapshot_date) - InventorySnapshot.received_at).label("age_days")
        statement = (
            select(
                Product.name,
                Warehouse.name,
                InventorySnapshot.snapshot_date,
                InventorySnapshot.on_hand_quantity,
                InventorySnapshot.reserved_quantity,
                (
                    InventorySnapshot.on_hand_quantity - InventorySnapshot.reserved_quantity
                ).label("available_quantity"),
                age_days,
            )
            .join(Product, Product.id == InventorySnapshot.product_id)
            .join(Warehouse, Warehouse.id == InventorySnapshot.warehouse_id)
            .where(InventorySnapshot.snapshot_date == snapshot_date)
            .order_by(Product.name, Warehouse.name)
        )
        if product_name:
            statement = statement.where(Product.name == product_name)
        if warehouse_name:
            statement = statement.where(Warehouse.name == warehouse_name)
        rows = (await self.session.execute(statement)).all()
        return [
            (row[0], row[1], row[2], int(row[3]), int(row[4]), int(row[5]), int(row[6]))
            for row in rows
        ]

    async def get_exposure(
        self, age_threshold_days: int, as_of_date: date
    ) -> tuple[int, int, int]:
        age_days = literal(as_of_date) - InventorySnapshot.received_at
        statement = (
            select(
                func.count(func.distinct(InventorySnapshot.product_id)).label("product_count"),
                func.coalesce(func.sum(InventorySnapshot.on_hand_quantity), 0).label(
                    "stock_quantity"
                ),
                func.coalesce(func.max(age_days), 0).label("oldest_age_days"),
            )
            .where(
                InventorySnapshot.snapshot_date == as_of_date,
                InventorySnapshot.received_at
                < as_of_date - timedelta(days=age_threshold_days),
                InventorySnapshot.on_hand_quantity > 0,
            )
        )
        row = (await self.session.execute(statement)).one()
        return int(row.product_count), int(row.stock_quantity), int(row.oldest_age_days)
