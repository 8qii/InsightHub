from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.domain.intelligence.models import Evidence, Signal, SuggestedQuestion


class ExecutiveSummary(BaseModel):
    net_revenue: Decimal
    gross_margin: Decimal
    gross_margin_rate: Decimal
    return_rate: Decimal
    inventory_risk_products: int
    inventory_risk_units: int


class BusinessDriver(BaseModel):
    driver: Literal["Sales", "Returns", "Discounts", "Inventory"]
    status: Literal["positive", "watch", "risk"]
    summary: str
    metric: str


PrioritySignal = Signal
EvidencePreview = Evidence
SuggestedInvestigation = SuggestedQuestion


class OverviewResponse(BaseModel):
    period: str
    scope: str
    as_of_date: date
    summary: ExecutiveSummary
    signals: list[PrioritySignal]
    drivers: list[BusinessDriver]
    evidence: list[EvidencePreview]
    investigations: list[SuggestedInvestigation]
