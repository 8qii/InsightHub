from datetime import date, timedelta

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models import Inventory, Product


class InventoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_risk(self, age_threshold_days: int) -> list[tuple[str, int, int]]:
        age_days = (func.current_date() - cast(Inventory.updated_at, Date)).label("age_days")
        cutoff = date.today() - timedelta(days=age_threshold_days)
        statement = (
            select(Product.name, Inventory.stock_quantity, age_days)
            .join(Inventory, Inventory.product_id == Product.id)
            .where(Inventory.updated_at < cutoff)
            .order_by(age_days.desc(), Product.name)
        )
        rows = (await self.session.execute(statement)).all()
        return [(row.name, int(row.stock_quantity), int(row.age_days)) for row in rows]
