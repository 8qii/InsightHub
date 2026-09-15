from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models import Order, OrderItem, Product, Return


class SalesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_summary(
        self, product_name: str, start_date: date, end_date: date
    ) -> tuple[str, Decimal, int] | None:
        line_revenue = OrderItem.quantity * OrderItem.unit_price - OrderItem.discount_amount
        statement = (
            select(
                Product.name,
                func.coalesce(func.sum(line_revenue), 0).label("revenue"),
                func.count(func.distinct(Order.id)).label("order_count"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
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

    async def get_performance(
        self,
        start_date: date,
        end_date: date,
        product_name: str | None,
        region: str | None,
        sales_channel: str | None,
    ) -> list[tuple[str, str, str, Decimal, Decimal, int, int, Decimal, Decimal]]:
        refunds = (
            select(Return.order_item_id, func.sum(Return.refund_amount).label("refund_amount"))
            .group_by(Return.order_item_id)
            .subquery()
        )
        gross_line_revenue = OrderItem.quantity * OrderItem.unit_price
        net_line_revenue = gross_line_revenue - OrderItem.discount_amount
        gross_revenue = func.sum(gross_line_revenue)
        net_revenue = func.sum(net_line_revenue - func.coalesce(refunds.c.refund_amount, 0))
        gross_margin = func.sum(
            net_line_revenue - func.coalesce(refunds.c.refund_amount, 0) - OrderItem.cost_basis
        )
        order_count = func.count(func.distinct(Order.id))
        statement = (
            select(
                Product.name,
                Order.region,
                Order.sales_channel,
                func.coalesce(gross_revenue, 0).label("gross_revenue"),
                func.coalesce(net_revenue, 0).label("net_revenue"),
                func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold"),
                order_count.label("order_count"),
                func.coalesce(
                    gross_revenue / func.nullif(order_count, 0), 0
                ).label("average_order_value"),
                func.coalesce(gross_margin, 0).label("gross_margin"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .outerjoin(refunds, refunds.c.order_item_id == OrderItem.id)
            .where(Order.order_date >= start_date, Order.order_date < end_date)
            .group_by(Product.name, Order.region, Order.sales_channel)
            .order_by(Product.name, Order.region, Order.sales_channel)
        )
        if product_name:
            statement = statement.where(Product.name == product_name)
        if region:
            statement = statement.where(Order.region == region)
        if sales_channel:
            statement = statement.where(Order.sales_channel == sales_channel)
        rows = (await self.session.execute(statement)).all()
        return [
            (
                row.name,
                row.region,
                row.sales_channel,
                Decimal(row.gross_revenue),
                Decimal(row.net_revenue),
                int(row.units_sold),
                int(row.order_count),
                Decimal(row.average_order_value),
                Decimal(row.gross_margin),
            )
            for row in rows
        ]

    async def get_returns_summary(
        self, start_date: date, end_date: date, product_name: str | None
    ) -> tuple[str | None, int, Decimal, Decimal]:
        return_rows = (
            select(
                Return.order_item_id,
                func.sum(Return.returned_quantity).label("returned_quantity"),
                func.sum(Return.refund_amount).label("refund_amount"),
            )
            .group_by(Return.order_item_id)
            .subquery()
        )
        sold_units = func.coalesce(func.sum(OrderItem.quantity), 0)
        statement = (
            select(
                func.coalesce(func.sum(return_rows.c.returned_quantity), 0).label("returned_units"),
                func.coalesce(func.sum(return_rows.c.refund_amount), 0).label("refund_amount"),
                sold_units.label("sold_units"),
            )
            .select_from(OrderItem)
            .join(Product, Product.id == OrderItem.product_id)
            .join(Order, Order.id == OrderItem.order_id)
            .outerjoin(return_rows, return_rows.c.order_item_id == OrderItem.id)
            .where(Order.order_date >= start_date, Order.order_date < end_date)
        )
        if product_name:
            statement = statement.where(Product.name == product_name)
        row = (await self.session.execute(statement)).one()
        returned_units = int(row.returned_units)
        return_rate = (
            Decimal(returned_units) / int(row.sold_units) if row.sold_units else Decimal("0")
        )
        return product_name, returned_units, Decimal(row.refund_amount), return_rate
