import asyncio
from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.api.overview import get_overview_service
from app.main import app
from app.tools.discount.models import DiscountViolations
from app.tools.inventory.models import InventoryExposure
from app.tools.overview.models import OverviewResponse
from app.tools.overview.service import OverviewService
from app.tools.sales.models import ReturnsSummary, SalesPerformance, SalesSummary


class FakeSalesService:
    async def get_sales_performance(
        self,
        start_date: date,
        end_date: date,
        product_name: str | None,
        region: str | None,
        sales_channel: str | None,
    ) -> list[SalesPerformance]:
        assert (start_date, end_date, product_name, region, sales_channel) == (
            date(2025, 7, 1),
            date(2025, 10, 1),
            None,
            None,
            None,
        )
        return [
            SalesPerformance(
                product="Product Luna",
                region="Midwest",
                sales_channel="Web",
                gross_revenue=Decimal("300000.00"),
                net_revenue=Decimal("246000.00"),
                units_sold=2460,
                order_count=2460,
                average_order_value=Decimal("121.95"),
                gross_margin=Decimal("82000.00"),
            )
        ]

    async def get_returns_summary(
        self, start_date: date, end_date: date, product_name: str | None
    ) -> ReturnsSummary:
        assert (start_date, end_date, product_name) == (
            date(2025, 7, 1),
            date(2025, 10, 1),
            None,
        )
        return ReturnsSummary(
            product=None,
            returned_units=200,
            refund_amount=Decimal("20000.00"),
            return_rate=Decimal("0.08"),
        )

    async def get_sales_summary(self, product_name: str, quarter: str) -> SalesSummary:
        revenue = Decimal("300000.00") if quarter == "Q2" else Decimal("246000.00")
        return SalesSummary(
            product=product_name, quarter=quarter, revenue=revenue, order_count=2460
        )


class FakeInventoryService:
    async def get_inventory_exposure(
        self, age_threshold_days: int, as_of_date: date
    ) -> InventoryExposure:
        assert (age_threshold_days, as_of_date) == (90, date(2025, 9, 30))
        return InventoryExposure(product_count=1, stock_quantity=12000, oldest_age_days=138)


class FakeDiscountService:
    async def get_discount_violations(
        self,
        threshold_percent: Decimal | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> DiscountViolations:
        assert threshold_percent is None
        assert (start_date, end_date) == (date(2025, 7, 1), date(2025, 10, 1))
        return DiscountViolations(total_violations=180, unapproved_violations=120)


def build_overview() -> OverviewResponse:
    service = OverviewService(
        FakeSalesService(),  # type: ignore[arg-type]
        FakeInventoryService(),  # type: ignore[arg-type]
        FakeDiscountService(),  # type: ignore[arg-type]
    )
    return asyncio.run(service.get_overview())


def test_overview_service_aggregates_decision_metrics() -> None:
    result = build_overview()

    assert result.period == "Q3 2025"
    assert result.scope == "All products"
    assert result.summary.net_revenue == Decimal("246000.00")
    assert result.summary.gross_margin == Decimal("82000.00")
    assert result.summary.return_rate == Decimal("0.08")
    assert result.summary.inventory_risk_products == 1
    assert result.summary.inventory_risk_units == 12000
    assert result.signals[0].metric == "18.0% quarter over quarter"
    assert {driver.driver for driver in result.drivers} == {
        "Sales",
        "Returns",
        "Discounts",
        "Inventory",
    }


def test_overview_endpoint_returns_typed_curated_contract() -> None:
    overview = build_overview()

    class FakeOverviewService:
        async def get_overview(self) -> OverviewResponse:
            return overview

    app.dependency_overrides[get_overview_service] = FakeOverviewService
    try:
        response = TestClient(app).get("/api/v1/overview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["net_revenue"] == "246000.00"
    assert body["signals"][0]["signal_id"] == "luna-revenue-decline"
    assert body["evidence"][0]["source_type"] == "document"
    assert body["evidence"][0]["role"] == "supporting_context"
    assert "rows" not in body
    assert "sql" not in body
