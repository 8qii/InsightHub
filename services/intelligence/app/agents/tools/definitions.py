from decimal import Decimal
from typing import cast

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.core.models import ToolContext, ToolDefinition
from app.errors import AppError
from app.tools.discount.models import DiscountViolations
from app.tools.discount.repository import DiscountRepository
from app.tools.discount.service import DiscountService
from app.tools.inventory.models import InventoryRisk
from app.tools.inventory.repository import InventoryRepository
from app.tools.inventory.service import InventoryService
from app.tools.knowledge.service import KnowledgeService
from app.tools.sales.models import SalesSummary
from app.tools.sales.repository import SalesRepository
from app.tools.sales.service import SalesService


class KnowledgeToolInput(BaseModel):
    query: str = Field(min_length=1, max_length=10_000)


class SalesToolInput(BaseModel):
    product_name: str = Field(min_length=1, max_length=200)
    quarter: str = Field(pattern=r"^Q[1-4]$")


class InventoryToolInput(BaseModel):
    age_threshold_days: int = Field(default=90, ge=1, le=3650)


class DiscountToolInput(BaseModel):
    maximum_discount: Decimal = Field(default=Decimal("12"), ge=0, le=100)


def build_tool_definitions(
    knowledge_service: KnowledgeService,
    workspace_id: str | None,
    session: AsyncSession | None,
) -> list[ToolDefinition]:
    async def search_knowledge(arguments: BaseModel, context: ToolContext) -> dict[str, object]:
        if not workspace_id:
            raise AppError(503, "knowledge_not_configured", "Knowledge search is not configured.")
        payload = cast(KnowledgeToolInput, arguments)
        result = await knowledge_service.query(workspace_id, payload.query, context.request_id)
        return {
            "answer": result.answer,
            "sources": [source.model_dump(mode="json") for source in result.sources],
        }

    async def get_sales(arguments: BaseModel, _: ToolContext) -> SalesSummary:
        if session is None:
            raise AppError(503, "database_unavailable", "The data service is not configured.")
        payload = cast(SalesToolInput, arguments)
        return await SalesService(SalesRepository(session)).get_sales_summary(
            payload.product_name.strip(), payload.quarter
        )

    async def get_inventory(arguments: BaseModel, _: ToolContext) -> list[InventoryRisk]:
        if session is None:
            raise AppError(503, "database_unavailable", "The data service is not configured.")
        payload = cast(InventoryToolInput, arguments)
        return await InventoryService(InventoryRepository(session)).get_inventory_risk(
            payload.age_threshold_days
        )

    async def get_discounts(arguments: BaseModel, _: ToolContext) -> DiscountViolations:
        if session is None:
            raise AppError(503, "database_unavailable", "The data service is not configured.")
        payload = cast(DiscountToolInput, arguments)
        return await DiscountService(DiscountRepository(session)).get_discount_violations(
            payload.maximum_discount
        )

    return [
        ToolDefinition(
            name="search_company_knowledge",
            description="Search company documents and return an answer with source citations.",
            input_schema=KnowledgeToolInput,
            execute=search_knowledge,
        ),
        ToolDefinition(
            name="get_sales_summary",
            description="Get revenue and order count for a product and quarter.",
            input_schema=SalesToolInput,
            execute=get_sales,
        ),
        ToolDefinition(
            name="get_inventory_risk",
            description="Find products whose inventory age is at or above the requested threshold.",
            input_schema=InventoryToolInput,
            execute=get_inventory,
        ),
        ToolDefinition(
            name="get_discount_violations",
            description="Count orders above the permitted discount and the unapproved subset.",
            input_schema=DiscountToolInput,
            execute=get_discounts,
        ),
    ]
