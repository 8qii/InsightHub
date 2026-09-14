from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SalesSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product: str
    quarter: str
    revenue: Decimal
    order_count: int
