from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models import DiscountEvent, Order


class DiscountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_violations(
        self,
        maximum_discount: Decimal,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[int, int]:
        conditions = [DiscountEvent.discount_percent > maximum_discount]
        if start_date is not None:
            conditions.append(Order.order_date >= start_date)
        if end_date is not None:
            conditions.append(Order.order_date < end_date)

        total_statement = select(func.count(DiscountEvent.id)).join(Order).where(*conditions)
        unapproved_statement = total_statement.where(DiscountEvent.approved.is_(False))
        total = (await self.session.execute(total_statement)).scalar_one()
        unapproved = (await self.session.execute(unapproved_statement)).scalar_one()
        return int(total), int(unapproved)
