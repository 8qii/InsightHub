from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from app.errors import AppError
from app.tools.sales.models import ReturnsSummary, SalesPerformance, SalesSummary
from app.tools.sales.repository import SalesRepository


class SalesService:
    def __init__(self, repository: SalesRepository) -> None:
        self.repository = repository

    async def get_sales_summary(self, product_name: str, quarter: str) -> SalesSummary:
        quarter_number = int(quarter[1:])
        start_month = (quarter_number - 1) * 3 + 1
        start_date = date(2025, start_month, 1)
        end_month = start_month + 2
        end_date = date(
            2025 if end_month < 12 else 2026,
            end_month + 1 if end_month < 12 else 1,
            1,
        )
        try:
            result = await self.repository.get_summary(product_name, start_date, end_date)
        except SQLAlchemyError as exc:
            raise AppError(503, "database_unavailable", "The data service is unavailable.") from exc
        if result is None:
            raise AppError(
                404,
                "sales_not_found",
                "No sales data was found for that product and quarter.",
            )
        product, revenue, order_count = result
        return SalesSummary(
            product=product,
            quarter=quarter,
            revenue=revenue,
            order_count=order_count,
        )

    async def get_sales_performance(
        self,
        start_date: date,
        end_date: date,
        product_name: str | None,
        region: str | None,
        sales_channel: str | None,
    ) -> list[SalesPerformance]:
        try:
            rows = await self.repository.get_performance(
                start_date, end_date, product_name, region, sales_channel
            )
        except SQLAlchemyError as exc:
            raise AppError(503, "database_unavailable", "The data service is unavailable.") from exc
        return [
            SalesPerformance(
                product=row[0],
                region=row[1],
                sales_channel=row[2],
                gross_revenue=row[3],
                net_revenue=row[4],
                units_sold=row[5],
                order_count=row[6],
                average_order_value=row[7],
                gross_margin=row[8],
            )
            for row in rows
        ]

    async def get_returns_summary(
        self, start_date: date, end_date: date, product_name: str | None
    ) -> ReturnsSummary:
        try:
            result = await self.repository.get_returns_summary(start_date, end_date, product_name)
        except SQLAlchemyError as exc:
            raise AppError(503, "database_unavailable", "The data service is unavailable.") from exc
        product, returned_units, refund_amount, return_rate = result
        return ReturnsSummary(
            product=product,
            returned_units=returned_units,
            refund_amount=refund_amount,
            return_rate=return_rate,
        )
