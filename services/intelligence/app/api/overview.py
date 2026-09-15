from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.session import get_db_session
from app.tools.discount.repository import DiscountRepository
from app.tools.discount.service import DiscountService
from app.tools.inventory.repository import InventoryRepository
from app.tools.inventory.service import InventoryService
from app.tools.overview.models import OverviewResponse
from app.tools.overview.service import OverviewService
from app.tools.sales.repository import SalesRepository
from app.tools.sales.service import SalesService

router = APIRouter(prefix="/api/v1", tags=["overview"])


async def get_overview_service(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> OverviewService:
    return OverviewService(
        sales_service=SalesService(SalesRepository(session)),
        inventory_service=InventoryService(InventoryRepository(session)),
        discount_service=DiscountService(DiscountRepository(session)),
    )


@router.get("/overview", response_model=OverviewResponse)
async def overview(
    service: OverviewService = Depends(get_overview_service),  # noqa: B008
) -> OverviewResponse:
    return await service.get_overview()
