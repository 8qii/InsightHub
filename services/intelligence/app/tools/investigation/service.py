from datetime import date
from decimal import Decimal

from app.errors import AppError
from app.tools.inventory.service import InventoryService
from app.tools.investigation.models import (
    Driver,
    Evidence,
    Finding,
    Investigation,
    SuggestedQuestion,
)
from app.tools.sales.service import SalesService

LUNA_REVENUE_DECLINE_ID = "luna-revenue-decline"
LUNA_PRODUCT = "Product Luna"
Q3_START = date(2025, 7, 1)
Q3_END = date(2025, 10, 1)
OVERVIEW_DATE = date(2025, 9, 30)
INVENTORY_AGE_THRESHOLD_DAYS = 90


class InvestigationService:
    def __init__(
        self, sales_service: SalesService, inventory_service: InventoryService
    ) -> None:
        self.sales_service = sales_service
        self.inventory_service = inventory_service

    async def get_investigation(self, investigation_id: str) -> Investigation:
        if investigation_id != LUNA_REVENUE_DECLINE_ID:
            raise AppError(
                404,
                "investigation_not_found",
                "No investigation was found for that signal.",
            )

        luna_q2 = await self.sales_service.get_sales_summary(LUNA_PRODUCT, "Q2")
        luna_q3 = await self.sales_service.get_sales_summary(LUNA_PRODUCT, "Q3")
        luna_returns = await self.sales_service.get_returns_summary(
            Q3_START, Q3_END, LUNA_PRODUCT
        )
        inventory_risk = await self.inventory_service.get_inventory_risk(
            INVENTORY_AGE_THRESHOLD_DAYS, OVERVIEW_DATE
        )
        luna_inventory = next(
            (risk for risk in inventory_risk if risk.product == LUNA_PRODUCT), None
        )
        revenue_delta = luna_q3.revenue - luna_q2.revenue
        revenue_decline = (
            (luna_q2.revenue - luna_q3.revenue) / luna_q2.revenue
            if luna_q2.revenue
            else Decimal("0")
        )

        inventory_summary = (
            f"{luna_inventory.stock_quantity:,} units at {luna_inventory.age_days} days old"
            if luna_inventory
            else "No stock older than 90 days in the Sep 30 snapshot"
        )
        inventory_detail = (
            "Product Luna has stock older than the risk threshold, which can limit a "
            "recovery response."
            if luna_inventory
            else "The Sep 30 snapshot does not show Product Luna stock older than 90 days."
        )

        return Investigation(
            investigation_id=LUNA_REVENUE_DECLINE_ID,
            title="Product Luna revenue decline",
            period="Q3 2025",
            as_of_date=OVERVIEW_DATE,
            executive_summary=(
                f"Product Luna Q3 revenue was ${luna_q3.revenue:,.0f}, down "
                f"{revenue_decline:.1%} from Q2. Review demand, returns, and available "
                "inventory before selecting a commercial response."
            ),
            conclusion=(
                "Product Luna missed its Q2 revenue baseline in Q3. The current evidence "
                "supports a targeted demand and product-performance review, rather than a "
                "single-cause conclusion."
            ),
            impact=(
                f"${abs(revenue_delta):,.0f} less revenue than Q2 across "
                f"{luna_q3.order_count:,} Q3 orders."
            ),
            findings=[
                Finding(
                    title="Revenue declined quarter over quarter",
                    summary="Q3 finished below Product Luna's Q2 revenue baseline.",
                    metric=f"{revenue_decline:.1%} decline (${abs(revenue_delta):,.0f})",
                    severity="high",
                ),
                Finding(
                    title="Returns need product-level review",
                    summary="Returns reduce realized Product Luna revenue and may indicate a "
                    "post-purchase experience issue.",
                    metric=f"{luna_returns.return_rate:.1%} return rate",
                    severity="medium" if luna_returns.return_rate else "low",
                ),
                Finding(
                    title="Inventory response needs validation",
                    summary=inventory_detail,
                    metric=inventory_summary,
                    severity="medium" if luna_inventory else "low",
                ),
            ],
            drivers=[
                Driver(
                    area="Demand",
                    status="risk",
                    summary="Revenue was below the prior-quarter baseline, requiring channel and "
                    "customer-segment follow-up.",
                    metric=f"${luna_q3.revenue:,.0f} Q3 revenue",
                ),
                Driver(
                    area="Returns",
                    status="watch" if luna_returns.return_rate else "positive",
                    summary="Returned units lower realized revenue and should be checked against "
                    "product, fulfillment, and quality signals.",
                    metric=f"{luna_returns.return_rate:.1%} return rate",
                ),
                Driver(
                    area="Inventory",
                    status="risk" if luna_inventory else "positive",
                    summary=inventory_detail,
                    metric=inventory_summary,
                ),
                Driver(
                    area="Business context",
                    status="watch",
                    summary="The Q3 business review identifies Product Luna as a strategic product "
                    "line, increasing the priority of a validated recovery plan.",
                    metric="Strategic product line",
                ),
            ],
            evidence=[
                Evidence(
                    observed_on=date(2025, 6, 30),
                    source_type="database",
                    role="metric_source",
                    title="Q2 sales baseline",
                    detail=f"Product Luna recorded ${luna_q2.revenue:,.0f} across "
                    f"{luna_q2.order_count:,} orders.",
                ),
                Evidence(
                    observed_on=date(2025, 9, 30),
                    source_type="database",
                    role="metric_source",
                    title="Q3 sales and returns",
                    detail=f"Product Luna recorded ${luna_q3.revenue:,.0f} revenue with a "
                    f"{luna_returns.return_rate:.1%} return rate.",
                ),
                Evidence(
                    observed_on=OVERVIEW_DATE,
                    source_type="metric",
                    role="metric_source",
                    title="Inventory snapshot",
                    detail=inventory_summary,
                ),
                Evidence(
                    observed_on=date(2025, 7, 1),
                    source_type="document",
                    role="supporting_context",
                    title="Q3 Business Review",
                    detail=(
                        "Management context identifies Product Luna as a strategic product line."
                    ),
                ),
            ],
            suggested_questions=[
                SuggestedQuestion(
                    question="Which regions and sales channels explain Product Luna's Q3 decline?",
                    rationale="Separate broad demand weakness from a concentrated execution issue.",
                ),
                SuggestedQuestion(
                    question="What return reasons are most common for Product Luna?",
                    rationale=(
                        "Test whether returns point to a product, fulfillment, or expectation gap."
                    ),
                ),
                SuggestedQuestion(
                    question=(
                        "How does Product Luna inventory compare with its Q3 demand by warehouse?"
                    ),
                    rationale=(
                        "Determine whether stock placement or aging constrains the recovery plan."
                    ),
                ),
            ],
        )
