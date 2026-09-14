from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models import DiscountEvent


class DiscountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_violations(self, maximum_discount: Decimal) -> tuple[int, int]:
        total_statement = select(func.count(DiscountEvent.id)).where(
            DiscountEvent.discount_percent > maximum_discount
        )
        unapproved_statement = select(func.count(DiscountEvent.id)).where(
            DiscountEvent.discount_percent > maximum_discount,
            DiscountEvent.approved.is_(False),
        )
        total = (await self.session.execute(total_statement)).scalar_one()
        unapproved = (await self.session.execute(unapproved_statement)).scalar_one()
        return int(total), int(unapproved)
