from datetime import date

from pydantic import BaseModel, ConfigDict


class InventoryRisk(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product: str
    stock_quantity: int
    age_days: int


class InventorySnapshotSummary(BaseModel):
    product: str
    warehouse: str
    snapshot_date: date
    on_hand_quantity: int
    reserved_quantity: int
    available_quantity: int
    age_days: int
