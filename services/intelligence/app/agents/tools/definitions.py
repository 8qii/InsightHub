from datetime import date
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
    as_of_date: date | None = Field(
        default=None,
        description="Historical snapshot date. Omit only when current-date analysis is intended.",
    )


class DiscountToolInput(BaseModel):
    threshold_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Optional discount threshold percent. Omit to use the 12% policy default.",
    )


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
            payload.age_threshold_days, payload.as_of_date
        )

    async def get_discounts(arguments: BaseModel, _: ToolContext) -> DiscountViolations:
        if session is None:
            raise AppError(503, "database_unavailable", "The data service is not configured.")
        payload = cast(DiscountToolInput, arguments)
        threshold = (
            Decimal(str(payload.threshold_percent))
            if payload.threshold_percent is not None
            else None
        )
        return await DiscountService(DiscountRepository(session)).get_discount_violations(
            threshold
        )

    return [
        ToolDefinition(
            name="search_company_knowledge",
            description=(
                "Use for company policies, document facts, and citations. "
                "Input: query text. Example: query='VIP discount policy'."
            ),
            input_schema=KnowledgeToolInput,
            execute=search_knowledge,
        ),
        ToolDefinition(
            name="get_sales_summary",
            description=(
                "Use for numeric revenue and order counts when product and quarter are known. "
                "Inputs: product_name and quarter='Q1'|'Q2'|'Q3'|'Q4'. "
                "Example: Product Luna, Q3."
            ),
            input_schema=SalesToolInput,
            execute=get_sales,
        ),
        ToolDefinition(
            name="get_inventory_risk",
            description=(
                "Use for inventory age risk. Input age_threshold_days; optionally provide "
                "as_of_date for historical snapshots. Example: 90 days as of 2025-09-30."
            ),
            input_schema=InventoryToolInput,
            execute=get_inventory,
        ),
        ToolDefinition(
            name="get_discount_violations",
            description=(
                "Use to count discount violations. Optional threshold_percent overrides the "
                "12% policy default; omit it for the policy threshold. Example: 10.0."
            ),
            input_schema=DiscountToolInput,
            execute=get_discounts,
        ),
    ]
