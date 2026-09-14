from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from app.errors import AppError
from app.tools.discount.models import DiscountViolations
from app.tools.discount.repository import DiscountRepository


class DiscountService:
    def __init__(self, repository: DiscountRepository) -> None:
        self.repository = repository

    async def get_discount_violations(self, maximum_discount: Decimal) -> DiscountViolations:
        try:
            total, unapproved = await self.repository.get_violations(maximum_discount)
        except SQLAlchemyError as exc:
            raise AppError(503, "database_unavailable", "The data service is unavailable.") from exc
        return DiscountViolations(
            total_violations=total,
            unapproved_violations=unapproved,
        )
