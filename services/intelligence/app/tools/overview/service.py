from datetime import date
from decimal import Decimal

from app.tools.discount.service import DiscountService
from app.tools.inventory.service import InventoryService
from app.tools.overview.models import (
    BusinessDriver,
    EvidencePreview,
    ExecutiveSummary,
    OverviewResponse,
    PrioritySignal,
    SuggestedInvestigation,
)
from app.tools.sales.service import SalesService

Q2_START = date(2025, 4, 1)
Q3_START = date(2025, 7, 1)
Q3_END = date(2025, 10, 1)
OVERVIEW_DATE = date(2025, 9, 30)
INVENTORY_AGE_THRESHOLD_DAYS = 90
LUNA_PRODUCT = "Product Luna"


class OverviewService:
    def __init__(
        self,
        sales_service: SalesService,
        inventory_service: InventoryService,
        discount_service: DiscountService,
    ) -> None:
        self.sales_service = sales_service
        self.inventory_service = inventory_service
        self.discount_service = discount_service

    async def get_overview(self) -> OverviewResponse:
        performance = await self.sales_service.get_sales_performance(
            Q3_START, Q3_END, None, None, None
        )
        returns = await self.sales_service.get_returns_summary(Q3_START, Q3_END, None)
        inventory = await self.inventory_service.get_inventory_exposure(
            INVENTORY_AGE_THRESHOLD_DAYS, OVERVIEW_DATE
        )
        discounts = await self.discount_service.get_discount_violations(
            start_date=Q3_START, end_date=Q3_END
        )
        luna_q2 = await self.sales_service.get_sales_summary(LUNA_PRODUCT, "Q2")
        luna_q3 = await self.sales_service.get_sales_summary(LUNA_PRODUCT, "Q3")

        net_revenue = sum((row.net_revenue for row in performance), Decimal("0"))
        gross_margin = sum((row.gross_margin for row in performance), Decimal("0"))
        gross_margin_rate = gross_margin / net_revenue if net_revenue else Decimal("0")
        luna_decline = (
            (luna_q2.revenue - luna_q3.revenue) / luna_q2.revenue
            if luna_q2.revenue
            else Decimal("0")
        )

        return OverviewResponse(
            period="Q3 2025",
            scope="All products",
            as_of_date=OVERVIEW_DATE,
            summary=ExecutiveSummary(
                net_revenue=net_revenue,
                gross_margin=gross_margin,
                gross_margin_rate=gross_margin_rate,
                return_rate=returns.return_rate,
                inventory_risk_products=inventory.product_count,
                inventory_risk_units=inventory.stock_quantity,
            ),
            signals=[
                PrioritySignal(
                    signal_id="luna-revenue-decline",
                    severity="high",
                    title="Product Luna revenue declined",
                    summary=(
                        "Q3 revenue finished below Q2, creating a material gap for a strategic "
                        "product line."
                    ),
                    metric=f"{luna_decline:.1%} quarter over quarter",
                ),
                PrioritySignal(
                    signal_id="discount-compliance",
                    severity="high" if discounts.unapproved_violations else "low",
                    title="Discount compliance requires review",
                    summary=(
                        "Unapproved discounts above the policy threshold remain in the commercial "
                        "review queue."
                    ),
                    metric=f"{discounts.unapproved_violations:,} unapproved exceptions",
                ),
                PrioritySignal(
                    signal_id="inventory-aging",
                    severity="medium" if inventory.product_count else "low",
                    title="Aging inventory is tying up stock",
                    summary=(
                        "Products above the 90-day threshold may require demand, transfer, or "
                        "markdown decisions."
                    ),
                    metric=(
                        f"{inventory.product_count:,} products / "
                        f"{inventory.oldest_age_days:,} days oldest"
                    ),
                ),
            ],
            drivers=[
                BusinessDriver(
                    driver="Sales",
                    status="watch",
                    summary="Q3 demand is broad, but Product Luna underperformed its Q2 baseline.",
                    metric=f"${net_revenue:,.0f} net revenue",
                ),
                BusinessDriver(
                    driver="Returns",
                    status="watch" if returns.return_rate else "positive",
                    summary=(
                        "Returned units reduce realized revenue and should be reviewed by product."
                    ),
                    metric=f"{returns.return_rate:.1%} return rate",
                ),
                BusinessDriver(
                    driver="Discounts",
                    status="risk" if discounts.unapproved_violations else "positive",
                    summary="Policy exceptions are concentrated in discounts that lack approval.",
                    metric=f"{discounts.total_violations:,} total violations",
                ),
                BusinessDriver(
                    driver="Inventory",
                    status="risk" if inventory.product_count else "positive",
                    summary="Aged stock increases working-capital and obsolescence exposure.",
                    metric=f"{inventory.stock_quantity:,} aged units",
                ),
            ],
            evidence=[
                EvidencePreview(
                    source_type="document",
                    role="supporting_context",
                    title="Q3 Business Review",
                    detail="Strategic product context and management priorities for Product Luna.",
                ),
                EvidencePreview(
                    source_type="document",
                    role="supporting_context",
                    title="Discount Policy",
                    detail="VIP discount threshold and approval requirements.",
                ),
                EvidencePreview(
                    source_type="database",
                    role="metric_source",
                    title="PostgreSQL sales and returns",
                    detail="Q3 order-item revenue, cost basis, refunds, and returned units.",
                ),
                EvidencePreview(
                    source_type="metric",
                    role="metric_source",
                    title="Inventory snapshot, Sep 30, 2025",
                    detail="Product-level stock age and quantity above the 90-day risk threshold.",
                ),
            ],
            investigations=[
                SuggestedInvestigation(
                    question="Why did Product Luna revenue decline in Q3?",
                    rationale=(
                        "Connect sales performance with business-plan and inventory evidence."
                    ),
                ),
                SuggestedInvestigation(
                    question="Which discount violations require immediate review?",
                    rationale=(
                        "Identify unapproved exceptions against the current policy threshold."
                    ),
                ),
                SuggestedInvestigation(
                    question="Which aging products create the greatest inventory exposure?",
                    rationale="Prioritize stock by age, quantity, and recent sales performance.",
                ),
            ],
        )
