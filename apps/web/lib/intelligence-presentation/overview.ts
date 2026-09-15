import type { Overview } from "@/lib/types";
import type {
  AttentionItemPresentation,
  EvidenceRelationshipPresentation,
  OverviewPresentation,
} from "./models";

function money(value: number | string) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Number(value));
}

function percent(value: number | string) {
  return new Intl.NumberFormat("en-US", {
    style: "percent",
    maximumFractionDigits: 1,
  }).format(Number(value));
}

function evidenceLabel(sourceType: "document" | "database" | "metric") {
  if (sourceType === "document") return "Document evidence";
  if (sourceType === "database") return "Database evidence";
  return "Metric evidence";
}

function evidenceRole(role: "supporting_context" | "metric_source") {
  return role === "metric_source" ? "Calculated input" : "Supporting context";
}

function createAttention(overview: Overview): AttentionItemPresentation[] {
  const evidenceCount = overview.evidence.length;
  return overview.signals.map((signal) => ({
    id: signal.signal_id,
    severity: signal.severity,
    title: signal.title,
    observation: signal.summary,
    impact: signal.metric,
    action: "Open investigation",
    actionHref: `/dashboard/investigations/${encodeURIComponent(signal.signal_id)}`,
    evidenceCount,
  }));
}

function createEvidenceRelationship(
  finding: string,
  overview: Overview,
): EvidenceRelationshipPresentation {
  return {
    finding,
    supportingEvidence: overview.evidence.map((evidence, index) => ({
      id: `${evidence.source_type}-${index}`,
      sourceType: evidence.source_type,
      sourceLabel: evidenceLabel(evidence.source_type),
      roleLabel: evidenceRole(evidence.role),
      title: evidence.title,
      detail: evidence.detail,
    })),
  };
}

export function createOverviewPresentation(overview: Overview): OverviewPresentation {
  const attention = createAttention(overview);
  const lead = attention[0];
  const evidenceCount = overview.evidence.length;
  const company = overview.scope;
  const insight = lead ? {
    headline: lead.title,
    observation: lead.observation,
    summary: lead.observation,
    impact: lead.impact,
    recommendation: lead.action,
    recommendationHref: lead.actionHref,
    confidence: evidenceCount ? "Evidence-backed" : "Evidence pending",
    evidenceCount,
    evidenceSummary: evidenceCount
      ? `${evidenceCount} source${evidenceCount === 1 ? "" : "s"} prepared for review.`
      : "No evidence sources are available for this observation.",
    priority: lead.severity,
  } : null;

  return {
    company,
    period: overview.period,
    scope: overview.scope,
    asOfDate: overview.as_of_date,
    evidenceCount,
    preparationStatus: insight ? "Analyst briefing prepared" : "No executive signals prepared",
    insight,
    attention,
    evidenceRelationship: createEvidenceRelationship(
      lead?.title ?? "No executive finding is available",
      overview,
    ),
    metrics: [
      { label: "Net revenue", value: money(overview.summary.net_revenue), detail: `${overview.period} after discounts and refunds` },
      { label: "Gross margin", value: money(overview.summary.gross_margin), detail: `${percent(overview.summary.gross_margin_rate)} of net revenue` },
      { label: "Return rate", value: percent(overview.summary.return_rate), detail: "Returned units in the reporting period" },
      { label: "Inventory risk", value: overview.summary.inventory_risk_products.toLocaleString(), detail: "Products with aged stock" },
    ],
  };
}
