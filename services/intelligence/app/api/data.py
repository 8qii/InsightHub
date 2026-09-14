from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.session import get_db_session
from app.tools.discount.models import DiscountViolations
from app.tools.discount.repository import DiscountRepository
from app.tools.discount.service import DiscountService
from app.tools.inventory.models import InventoryRisk
from app.tools.inventory.repository import InventoryRepository
from app.tools.inventory.service import InventoryService
from app.tools.sales.models import SalesSummary
from app.tools.sales.repository import SalesRepository
from app.tools.sales.service import SalesService

router = APIRouter(prefix="/api/v1/data", tags=["data"])


async def get_sales_service(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> SalesService:
    return SalesService(SalesRepository(session))


async def get_inventory_service(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> InventoryService:
    return InventoryService(InventoryRepository(session))


async def get_discount_service(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> DiscountService:
    return DiscountService(DiscountRepository(session))


@router.get("/sales/summary", response_model=SalesSummary)
async def sales_summary(
    product_name: str = Query(..., min_length=1, max_length=200),  # noqa: B008
    quarter: str = Query(..., pattern=r"^Q[1-4]$"),  # noqa: B008
    service: SalesService = Depends(get_sales_service),  # noqa: B008
) -> SalesSummary:
    return await service.get_sales_summary(product_name.strip(), quarter)


@router.get("/inventory/risk", response_model=list[InventoryRisk])
async def inventory_risk(
    age_threshold_days: int = Query(..., ge=1, le=3650),  # noqa: B008
    as_of_date: date | None = Query(default=None),  # noqa: B008
    service: InventoryService = Depends(get_inventory_service),  # noqa: B008
) -> list[InventoryRisk]:
    return await service.get_inventory_risk(age_threshold_days, as_of_date)


@router.get("/discount/violations", response_model=DiscountViolations)
async def discount_violations(
    threshold_percent: float | None = Query(default=None, ge=0, le=100),  # noqa: B008
    service: DiscountService = Depends(get_discount_service),  # noqa: B008
) -> DiscountViolations:
    threshold = Decimal(str(threshold_percent)) if threshold_percent is not None else None
    return await service.get_discount_violations(threshold)
