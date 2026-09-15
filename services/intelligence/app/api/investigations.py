from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.session import get_db_session
from app.domain.intelligence import Investigation
from app.tools.inventory.repository import InventoryRepository
from app.tools.inventory.service import InventoryService
from app.tools.investigation.service import InvestigationService
from app.tools.sales.repository import SalesRepository
from app.tools.sales.service import SalesService

router = APIRouter(prefix="/api/v1/investigations", tags=["investigations"])


async def get_investigation_service(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> InvestigationService:
    return InvestigationService(
        sales_service=SalesService(SalesRepository(session)),
        inventory_service=InventoryService(InventoryRepository(session)),
    )


@router.get("/{investigation_id}", response_model=Investigation)
async def investigation(
    investigation_id: str,
    service: InvestigationService = Depends(get_investigation_service),  # noqa: B008
) -> Investigation:
    return await service.get_investigation(investigation_id)
