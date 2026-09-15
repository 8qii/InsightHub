export type Citation = {
  source?: string;
  title?: string;
  content?: string;
  text?: string;
  [key: string]: unknown;
};

export type AgentResponse = {
  answer: string;
  sources: Citation[];
};

export type AgentRunTool = {
  name: string;
  duration_ms: number;
  status: string;
};

export type AgentRun = {
  run_id: string;
  status: string;
  duration_ms: number;
  tools: AgentRunTool[];
};

export type SalesSummary = {
  product: string;
  quarter: string;
  revenue: number | string;
  order_count: number;
};

export type InventoryRisk = {
  product: string;
  stock_quantity: number;
  age_days: number;
};

export type DiscountViolations = {
  total_violations: number;
  unapproved_violations: number;
};

export type OverviewSummary = {
  net_revenue: number | string;
  gross_margin: number | string;
  gross_margin_rate: number | string;
  return_rate: number | string;
  inventory_risk_products: number;
  inventory_risk_units: number;
};

export type PrioritySignal = {
  signal_id: string;
  severity: "high" | "medium" | "low";
  title: string;
  summary: string;
  metric: string;
};

export type BusinessDriver = {
  driver: "Sales" | "Returns" | "Discounts" | "Inventory";
  status: "positive" | "watch" | "risk";
  summary: string;
  metric: string;
};

export type EvidencePreview = {
  source_type: "document" | "database" | "metric";
  role: "supporting_context" | "metric_source";
  title: string;
  detail: string;
};

export type SuggestedInvestigation = {
  question: string;
  rationale: string;
};

export type Overview = {
  period: string;
  scope: string;
  as_of_date: string;
  summary: OverviewSummary;
  signals: PrioritySignal[];
  drivers: BusinessDriver[];
  evidence: EvidencePreview[];
  investigations: SuggestedInvestigation[];
};

export type InvestigationFinding = {
  title: string;
  summary: string;
  metric: string;
  severity: "high" | "medium" | "low";
};

export type InvestigationDriver = {
  area: "Demand" | "Returns" | "Inventory" | "Business context";
  status: "positive" | "watch" | "risk";
  summary: string;
  metric: string;
};

export type InvestigationEvidence = {
  observed_on: string;
  source_type: "document" | "database" | "metric";
  role: "supporting_context" | "metric_source";
  title: string;
  detail: string;
};

export type SuggestedQuestion = {
  question: string;
  rationale: string;
};

export type Investigation = {
  investigation_id: string;
  title: string;
  period: string;
  as_of_date: string;
  executive_summary: string;
  conclusion: string;
  impact: string;
  findings: InvestigationFinding[];
  drivers: InvestigationDriver[];
  evidence: InvestigationEvidence[];
  suggested_questions: SuggestedQuestion[];
};

export type ApiError = Error & { status?: number };
