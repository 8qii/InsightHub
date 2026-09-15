import asyncio
from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.api.investigations import get_investigation_service
from app.errors import AppError
from app.main import app
from app.tools.inventory.models import InventoryRisk
from app.tools.investigation.models import Investigation
from app.tools.investigation.service import InvestigationService
from app.tools.sales.models import ReturnsSummary, SalesSummary


class FakeSalesService:
    async def get_sales_summary(self, product_name: str, quarter: str) -> SalesSummary:
        assert product_name == "Product Luna"
        revenue = Decimal("300000.00") if quarter == "Q2" else Decimal("246000.00")
        return SalesSummary(
            product=product_name, quarter=quarter, revenue=revenue, order_count=2460
        )

    async def get_returns_summary(
        self, start_date: date, end_date: date, product_name: str | None
    ) -> ReturnsSummary:
        assert (start_date, end_date, product_name) == (
            date(2025, 7, 1),
            date(2025, 10, 1),
            "Product Luna",
        )
        return ReturnsSummary(
            product=product_name,
            returned_units=200,
            refund_amount=Decimal("20000.00"),
            return_rate=Decimal("0.08"),
        )


class FakeInventoryService:
    async def get_inventory_risk(
        self, age_threshold_days: int, as_of_date: date
    ) -> list[InventoryRisk]:
        assert (age_threshold_days, as_of_date) == (90, date(2025, 9, 30))
        return [InventoryRisk(product="Product Luna", stock_quantity=12000, age_days=138)]


def build_investigation() -> Investigation:
    service = InvestigationService(
        FakeSalesService(),  # type: ignore[arg-type]
        FakeInventoryService(),  # type: ignore[arg-type]
    )
    return asyncio.run(service.get_investigation("luna-revenue-decline"))


def test_investigation_service_returns_curated_luna_contract() -> None:
    result = build_investigation()

    assert result.title == "Product Luna revenue decline"
    assert result.impact == "$54,000 less revenue than Q2 across 2,460 Q3 orders."
    assert result.findings[0].metric == "18.0% decline ($54,000)"
    assert result.drivers[2].metric == "12,000 units at 138 days old"
    assert result.evidence[0].role == "metric_source"
    assert result.evidence[-1].role == "supporting_context"


def test_investigation_service_rejects_unknown_signal() -> None:
    service = InvestigationService(
        FakeSalesService(),  # type: ignore[arg-type]
        FakeInventoryService(),  # type: ignore[arg-type]
    )

    try:
        asyncio.run(service.get_investigation("unknown"))
    except AppError as exc:
        assert exc.status_code == 404
        assert exc.code == "investigation_not_found"
    else:
        raise AssertionError("Unknown investigation should fail safely.")


def test_investigation_endpoint_hides_internal_details() -> None:
    investigation = build_investigation()

    class FakeInvestigationService:
        async def get_investigation(self, investigation_id: str) -> Investigation:
            assert investigation_id == "luna-revenue-decline"
            return investigation

    app.dependency_overrides[get_investigation_service] = FakeInvestigationService
    try:
        response = TestClient(app).get("/api/v1/investigations/luna-revenue-decline")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["investigation_id"] == "luna-revenue-decline"
    assert body["findings"][0]["severity"] == "high"
    assert body["evidence"][0]["source_type"] == "database"
    assert "rows" not in body
    assert "sql" not in body
    assert "repository" not in body
