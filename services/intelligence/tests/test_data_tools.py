import asyncio
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql

from app.api.data import (
    get_discount_service,
    get_inventory_service,
    get_sales_service,
)
from app.main import app
from app.tools.discount.models import DiscountViolations
from app.tools.discount.repository import DiscountRepository
from app.tools.discount.service import DiscountService
from app.tools.inventory.models import InventoryExposure, InventoryRisk, InventorySnapshotSummary
from app.tools.inventory.repository import InventoryRepository
from app.tools.inventory.service import InventoryService
from app.tools.sales.models import ReturnsSummary, SalesPerformance, SalesSummary


class FakeSalesService:
    async def get_sales_summary(self, product_name: str, quarter: str) -> SalesSummary:
        assert product_name == "Product Luna"
        assert quarter == "Q3"
        return SalesSummary(
            product=product_name,
            quarter=quarter,
            revenue=Decimal("246000.00"),
            order_count=2460,
        )


class FakeInventoryService:
    async def get_inventory_risk(
        self, age_threshold_days: int, as_of_date: date | None = None
    ) -> list[InventoryRisk]:
        assert age_threshold_days == 90
        assert as_of_date is None
        return [InventoryRisk(product="Product Luna", stock_quantity=12000, age_days=138)]


class HistoricalInventoryService:
    async def get_inventory_risk(
        self, age_threshold_days: int, as_of_date: date | None = None
    ) -> list[InventoryRisk]:
        assert age_threshold_days == 90
        assert as_of_date == date(2025, 9, 30)
        return [InventoryRisk(product="Product Luna", stock_quantity=12000, age_days=138)]


class FakeDiscountService:
    async def get_discount_violations(
        self, threshold_percent: Decimal | None
    ) -> DiscountViolations:
        assert threshold_percent in {None, Decimal("10")}
        return DiscountViolations(total_violations=180, unapproved_violations=120)


class FakeSalesPerformanceService:
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
            "Product Luna",
            "Midwest",
            "Web",
        )
        return [
            SalesPerformance(
                product="Product Luna",
                region="Midwest",
                sales_channel="Web",
                gross_revenue=Decimal("1000.00"),
                net_revenue=Decimal("940.00"),
                units_sold=10,
                order_count=8,
                average_order_value=Decimal("125.00"),
                gross_margin=Decimal("360.00"),
            )
        ]

    async def get_returns_summary(
        self, start_date: date, end_date: date, product_name: str | None
    ) -> ReturnsSummary:
        assert (start_date, end_date, product_name) == (
            date(2025, 7, 1),
            date(2025, 10, 1),
            "Product Luna",
        )
        return ReturnsSummary(
            product="Product Luna",
            returned_units=2,
            refund_amount=Decimal("60.00"),
            return_rate=Decimal("0.2"),
        )


class FakeInventorySnapshotService:
    async def get_inventory_snapshot(
        self, snapshot_date: date, product_name: str | None, warehouse_name: str | None
    ) -> list[InventorySnapshotSummary]:
        assert (snapshot_date, product_name, warehouse_name) == (
            date(2025, 9, 30),
            "Product Luna",
            "Central Hub",
        )
        return [
            InventorySnapshotSummary(
                product="Product Luna",
                warehouse="Central Hub",
                snapshot_date=snapshot_date,
                on_hand_quantity=12000,
                reserved_quantity=900,
                available_quantity=11100,
                age_days=138,
            )
        ]


def test_sales_endpoint_returns_typed_summary() -> None:
    app.dependency_overrides[get_sales_service] = FakeSalesService
    try:
        response = TestClient(app).get(
            "/api/v1/data/sales/summary",
            params={"product_name": "Product Luna", "quarter": "Q3"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "product": "Product Luna",
        "quarter": "Q3",
        "revenue": "246000.00",
        "order_count": 2460,
    }


def test_inventory_endpoint_returns_luna_risk() -> None:
    app.dependency_overrides[get_inventory_service] = FakeInventoryService
    try:
        response = TestClient(app).get(
            "/api/v1/data/inventory/risk", params={"age_threshold_days": 90}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["product"] == "Product Luna"
    assert response.json()[0]["age_days"] == 138


def test_inventory_endpoint_accepts_historical_as_of_date() -> None:
    app.dependency_overrides[get_inventory_service] = HistoricalInventoryService
    try:
        response = TestClient(app).get(
            "/api/v1/data/inventory/risk",
            params={"age_threshold_days": 90, "as_of_date": "2025-09-30"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0] == {
        "product": "Product Luna",
        "stock_quantity": 12000,
        "age_days": 138,
    }


def test_sales_performance_and_returns_endpoints_are_typed_and_bounded() -> None:
    app.dependency_overrides[get_sales_service] = FakeSalesPerformanceService
    try:
        client = TestClient(app)
        params = {
            "start_date": "2025-07-01",
            "end_date": "2025-10-01",
            "product_name": "Product Luna",
            "region": "Midwest",
            "sales_channel": "Web",
        }
        performance = client.get("/api/v1/data/sales/performance", params=params)
        return_params = {
            key: value
            for key, value in params.items()
            if key not in {"region", "sales_channel"}
        }
        returns = client.get(
            "/api/v1/data/returns/summary",
            params=return_params,
        )
    finally:
        app.dependency_overrides.clear()

    assert performance.status_code == 200
    assert performance.json()[0]["net_revenue"] == "940.00"
    assert returns.status_code == 200
    assert returns.json() == {
        "product": "Product Luna",
        "returned_units": 2,
        "refund_amount": "60.00",
        "return_rate": "0.2",
    }


def test_inventory_snapshots_endpoint_returns_available_inventory() -> None:
    app.dependency_overrides[get_inventory_service] = FakeInventorySnapshotService
    try:
        response = TestClient(app).get(
            "/api/v1/data/inventory/snapshots",
            params={
                "snapshot_date": "2025-09-30",
                "product_name": "Product Luna",
                "warehouse_name": "Central Hub",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["available_quantity"] == 11100


def test_discount_endpoint_returns_expected_violations() -> None:
    app.dependency_overrides[get_discount_service] = FakeDiscountService
    try:
        response = TestClient(app).get(
            "/api/v1/data/discount/violations"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"total_violations": 180, "unapproved_violations": 120}


def test_discount_endpoint_accepts_custom_threshold() -> None:
    app.dependency_overrides[get_discount_service] = FakeDiscountService
    try:
        response = TestClient(app).get(
            "/api/v1/data/discount/violations", params={"threshold_percent": "10"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200


def test_data_endpoints_validate_parameters() -> None:
    client = TestClient(app)
    app.dependency_overrides[get_sales_service] = FakeSalesService
    app.dependency_overrides[get_inventory_service] = FakeInventoryService
    app.dependency_overrides[get_discount_service] = FakeDiscountService
    try:
        assert client.get(
            "/api/v1/data/sales/summary",
            params={"product_name": "Luna", "quarter": "2025"},
        ).status_code == 422
        assert client.get(
            "/api/v1/data/sales/performance",
            params={
                "start_date": "2025-07-01",
                "end_date": "2025-10-01",
                "region": "Unknown",
            },
        ).status_code == 422
        assert client.get(
            "/api/v1/data/inventory/risk", params={"age_threshold_days": 0}
        ).status_code == 422
        assert client.get(
            "/api/v1/data/inventory/risk",
            params={"age_threshold_days": 90, "as_of_date": "not-a-date"},
        ).status_code == 422
        assert client.get(
            "/api/v1/data/discount/violations", params={"threshold_percent": 101}
        ).status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_services_are_awaitable() -> None:
    assert asyncio.iscoroutinefunction(FakeSalesService.get_sales_summary)
    assert asyncio.iscoroutinefunction(FakeInventoryService.get_inventory_risk)
    assert asyncio.iscoroutinefunction(FakeDiscountService.get_discount_violations)


def test_discount_service_uses_policy_default_or_custom_threshold() -> None:
    thresholds: list[Decimal] = []

    class Repository:
        async def get_violations(self, threshold: Decimal) -> tuple[int, int]:
            thresholds.append(threshold)
            return 180, 120

    service = DiscountService(Repository())  # type: ignore[arg-type]

    asyncio.run(service.get_discount_violations())
    asyncio.run(service.get_discount_violations(Decimal("10")))

    assert thresholds == [Decimal("12"), Decimal("10")]


def test_discount_service_passes_optional_reporting_period() -> None:
    periods: list[tuple[date | None, date | None]] = []

    class Repository:
        async def get_violations(
            self,
            threshold: Decimal,
            start_date: date | None = None,
            end_date: date | None = None,
        ) -> tuple[int, int]:
            assert threshold == Decimal("12")
            periods.append((start_date, end_date))
            return 20, 10

    service = DiscountService(Repository())  # type: ignore[arg-type]
    result = asyncio.run(
        service.get_discount_violations(
            start_date=date(2025, 7, 1), end_date=date(2025, 10, 1)
        )
    )

    assert periods == [(date(2025, 7, 1), date(2025, 10, 1))]
    assert result.total_violations == 20


def test_inventory_service_returns_aged_unit_exposure() -> None:
    class Repository:
        async def get_exposure(
            self, age_threshold_days: int, as_of_date: date
        ) -> tuple[int, int, int]:
            assert (age_threshold_days, as_of_date) == (90, date(2025, 9, 30))
            return 4, 18000, 138

    service = InventoryService(Repository())  # type: ignore[arg-type]
    result = asyncio.run(service.get_inventory_exposure(90, date(2025, 9, 30)))

    assert result == InventoryExposure(
        product_count=4, stock_quantity=18000, oldest_age_days=138
    )


def test_overview_repository_queries_enforce_period_and_aged_stock() -> None:
    statements: list[Any] = []

    class Row:
        product_count = 0
        stock_quantity = 0
        oldest_age_days = 0

    class Result:
        def scalar_one(self) -> int:
            return 0

        def one(self) -> Row:
            return Row()

    class Session:
        async def execute(self, statement: object) -> Result:
            statements.append(statement)
            return Result()

    discount_repository = DiscountRepository(Session())  # type: ignore[arg-type]
    inventory_repository = InventoryRepository(Session())  # type: ignore[arg-type]

    asyncio.run(
        discount_repository.get_violations(
            Decimal("12"), date(2025, 7, 1), date(2025, 10, 1)
        )
    )
    asyncio.run(inventory_repository.get_exposure(90, date(2025, 9, 30)))

    discount_sql = str(
        statements[0].compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )
    inventory_sql = str(
        statements[2].compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )
    assert "orders.order_date >= '2025-07-01'" in discount_sql
    assert "orders.order_date < '2025-10-01'" in discount_sql
    assert "inventory_snapshots.received_at < '2025-07-02'" in inventory_sql
    assert "inventory_snapshots.on_hand_quantity > 0" in inventory_sql
