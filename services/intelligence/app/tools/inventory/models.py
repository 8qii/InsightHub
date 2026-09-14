from pydantic import BaseModel, ConfigDict


class InventoryRisk(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product: str
    stock_quantity: int
    age_days: int
