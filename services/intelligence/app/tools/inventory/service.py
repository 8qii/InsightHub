from sqlalchemy.exc import SQLAlchemyError

from app.errors import AppError
from app.tools.inventory.models import InventoryRisk
from app.tools.inventory.repository import InventoryRepository


class InventoryService:
    def __init__(self, repository: InventoryRepository) -> None:
        self.repository = repository

    async def get_inventory_risk(self, age_threshold_days: int) -> list[InventoryRisk]:
        try:
            rows = await self.repository.get_risk(age_threshold_days)
        except SQLAlchemyError as exc:
            raise AppError(503, "database_unavailable", "The data service is unavailable.") from exc
        return [
            InventoryRisk(product=product, stock_quantity=stock, age_days=age)
            for product, stock, age in rows
        ]
