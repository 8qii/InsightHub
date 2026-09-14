import asyncio
from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.api.data import (
    get_discount_service,
    get_inventory_service,
    get_sales_service,
)
from app.main import app
from app.tools.discount.models import DiscountViolations
from app.tools.inventory.models import InventoryRisk
from app.tools.sales.models import SalesSummary


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
    async def get_discount_violations(self, maximum_discount: Decimal) -> DiscountViolations:
        assert maximum_discount == Decimal("12")
        return DiscountViolations(total_violations=180, unapproved_violations=120)


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


def test_discount_endpoint_returns_expected_violations() -> None:
    app.dependency_overrides[get_discount_service] = FakeDiscountService
    try:
        response = TestClient(app).get(
            "/api/v1/data/discount/violations", params={"maximum_discount": "12"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"total_violations": 180, "unapproved_violations": 120}


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
            "/api/v1/data/inventory/risk", params={"age_threshold_days": 0}
        ).status_code == 422
        assert client.get(
            "/api/v1/data/inventory/risk",
            params={"age_threshold_days": 90, "as_of_date": "not-a-date"},
        ).status_code == 422
        assert client.get(
            "/api/v1/data/discount/violations", params={"maximum_discount": 101}
        ).status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_services_are_awaitable() -> None:
    assert asyncio.iscoroutinefunction(FakeSalesService.get_sales_summary)
    assert asyncio.iscoroutinefunction(FakeInventoryService.get_inventory_risk)
    assert asyncio.iscoroutinefunction(FakeDiscountService.get_discount_violations)
