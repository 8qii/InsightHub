from datetime import date
from typing import Literal

from pydantic import BaseModel

Severity = Literal["high", "medium", "low"]
DriverStatus = Literal["positive", "watch", "risk"]
EvidenceSourceType = Literal["document", "database", "metric"]
EvidenceRole = Literal["supporting_context", "metric_source"]


class Insight(BaseModel):
    """A concise, display-safe intelligence observation."""

    title: str
    summary: str
    metric: str


class Signal(Insight):
    """A detected issue that can be investigated."""

    signal_id: str
    severity: Severity


class Finding(Insight):
    """A validated observation within an investigation."""

    severity: Severity


class Evidence(BaseModel):
    """Display-safe provenance for a calculated metric or supporting context."""

    source_type: EvidenceSourceType
    role: EvidenceRole
    title: str
    detail: str


class TimelineEvidence(Evidence):
    """Evidence with a known observation date for an investigation timeline."""

    observed_on: date


class SuggestedQuestion(BaseModel):
    question: str
    rationale: str


class InvestigationDriver(BaseModel):
    area: Literal["Demand", "Returns", "Inventory", "Business context"]
    status: DriverStatus
    summary: str
    metric: str


class Investigation(BaseModel):
    """A curated, decision-support investigation without raw operational records."""

    investigation_id: str
    title: str
    period: str
    as_of_date: date
    executive_summary: str
    conclusion: str
    impact: str
    findings: list[Finding]
    drivers: list[InvestigationDriver]
    evidence: list[TimelineEvidence]
    suggested_questions: list[SuggestedQuestion]
