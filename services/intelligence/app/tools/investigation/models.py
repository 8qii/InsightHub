"""Compatibility exports for the investigation tool contract."""

from app.domain.intelligence.models import (
    Finding,
    Investigation,
    InvestigationDriver,
    SuggestedQuestion,
    TimelineEvidence,
)

Driver = InvestigationDriver
Evidence = TimelineEvidence

__all__ = ["Driver", "Evidence", "Finding", "Investigation", "SuggestedQuestion"]
