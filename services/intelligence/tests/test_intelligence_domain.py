from datetime import date

import pytest
from pydantic import ValidationError

from app.domain.intelligence import (
    Evidence,
    Finding,
    Investigation,
    InvestigationDriver,
    Signal,
    SuggestedQuestion,
    TimelineEvidence,
)
from app.tools.investigation.models import Evidence as LegacyInvestigationEvidence
from app.tools.investigation.models import Investigation as LegacyInvestigation
from app.tools.overview.models import EvidencePreview, PrioritySignal


def test_domain_models_serialize_display_safe_intelligence() -> None:
    investigation = Investigation(
        investigation_id="luna-revenue-decline",
        title="Product Luna revenue decline",
        period="Q3 2025",
        as_of_date=date(2025, 9, 30),
        executive_summary="Revenue declined from Q2.",
        conclusion="Validate demand and returns before acting.",
        impact="$54,000 less revenue than Q2.",
        findings=[
            Finding(
                title="Revenue declined",
                summary="Q3 closed below Q2.",
                metric="18.0% decline",
                severity="high",
            )
        ],
        drivers=[
            InvestigationDriver(
                area="Demand",
                status="risk",
                summary="Demand needs validation.",
                metric="$246,000 Q3 revenue",
            )
        ],
        evidence=[
            TimelineEvidence(
                observed_on=date(2025, 9, 30),
                source_type="database",
                role="metric_source",
                title="Q3 sales",
                detail="Calculated sales performance.",
            )
        ],
        suggested_questions=[
            SuggestedQuestion(
                question="Which regions declined?",
                rationale="Identify the affected demand segments.",
            )
        ],
    )

    assert investigation.model_dump(mode="json") == {
        "investigation_id": "luna-revenue-decline",
        "title": "Product Luna revenue decline",
        "period": "Q3 2025",
        "as_of_date": "2025-09-30",
        "executive_summary": "Revenue declined from Q2.",
        "conclusion": "Validate demand and returns before acting.",
        "impact": "$54,000 less revenue than Q2.",
        "findings": [
            {
                "title": "Revenue declined",
                "summary": "Q3 closed below Q2.",
                "metric": "18.0% decline",
                "severity": "high",
            }
        ],
        "drivers": [
            {
                "area": "Demand",
                "status": "risk",
                "summary": "Demand needs validation.",
                "metric": "$246,000 Q3 revenue",
            }
        ],
        "evidence": [
            {
                "source_type": "database",
                "role": "metric_source",
                "title": "Q3 sales",
                "detail": "Calculated sales performance.",
                "observed_on": "2025-09-30",
            }
        ],
        "suggested_questions": [
            {
                "question": "Which regions declined?",
                "rationale": "Identify the affected demand segments.",
            }
        ],
    }


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (
            Signal,
            {
                "signal_id": "luna-revenue-decline",
                "severity": "urgent",
                "title": "Revenue declined",
                "summary": "Q3 declined.",
                "metric": "18.0%",
            },
        ),
        (
            Evidence,
            {
                "source_type": "query",
                "role": "metric_source",
                "title": "Sales",
                "detail": "Calculated result.",
            },
        ),
        (
            InvestigationDriver,
            {
                "area": "Pricing",
                "status": "risk",
                "summary": "Review pricing.",
                "metric": "12%",
            },
        ),
    ],
)
def test_domain_models_reject_invalid_enumerations(
    model: type[Signal] | type[Evidence] | type[InvestigationDriver], payload: dict[str, str]
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)


def test_legacy_contract_exports_use_shared_models() -> None:
    assert PrioritySignal is Signal
    assert EvidencePreview is Evidence
    assert LegacyInvestigation is Investigation
    assert LegacyInvestigationEvidence is TimelineEvidence
