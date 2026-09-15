from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from app.errors import AppError
from app.tools.inventory.models import InventoryRisk, InventorySnapshotSummary
from app.tools.inventory.repository import InventoryRepository


class InventoryService:
    def __init__(self, repository: InventoryRepository) -> None:
        self.repository = repository

    async def get_inventory_risk(
        self, age_threshold_days: int, as_of_date: date | None = None
    ) -> list[InventoryRisk]:
        try:
            rows = await self.repository.get_risk(age_threshold_days, as_of_date)
        except SQLAlchemyError as exc:
            raise AppError(503, "database_unavailable", "The data service is unavailable.") from exc
        return [
            InventoryRisk(product=product, stock_quantity=stock, age_days=age)
            for product, stock, age in rows
        ]

    async def get_inventory_snapshot(
        self, snapshot_date: date, product_name: str | None, warehouse_name: str | None
    ) -> list[InventorySnapshotSummary]:
        try:
            rows = await self.repository.get_snapshot(product_name, warehouse_name, snapshot_date)
        except SQLAlchemyError as exc:
            raise AppError(503, "database_unavailable", "The data service is unavailable.") from exc
        return [
            InventorySnapshotSummary(
                product=row[0], warehouse=row[1], snapshot_date=row[2], on_hand_quantity=row[3],
                reserved_quantity=row[4], available_quantity=row[5], age_days=row[6]
            )
            for row in rows
        ]
