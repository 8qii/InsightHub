from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models import Order, Product


class SalesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_summary(
        self, product_name: str, start_date: date, end_date: date
    ) -> tuple[str, Decimal, int] | None:
        statement = (
            select(
                Product.name,
                func.coalesce(func.sum(Order.amount), 0).label("revenue"),
                func.count(Order.id).label("order_count"),
            )
            .join(Order, Order.product_id == Product.id)
            .where(
                Product.name == product_name,
                Order.order_date >= start_date,
                Order.order_date < end_date,
            )
            .group_by(Product.name)
        )
        row = (await self.session.execute(statement)).one_or_none()
        if row is None:
            return None
        return row.name, Decimal(row.revenue), int(row.order_count)
