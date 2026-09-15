from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SalesSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product: str
    quarter: str
    revenue: Decimal
    order_count: int


class SalesPerformance(BaseModel):
    product: str
    region: str
    sales_channel: str
    gross_revenue: Decimal
    net_revenue: Decimal
    units_sold: int
    order_count: int
    average_order_value: Decimal
    gross_margin: Decimal


class ReturnsSummary(BaseModel):
    product: str | None
    returned_units: int
    refund_amount: Decimal
    return_rate: Decimal
