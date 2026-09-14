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

export type ApiError = Error & { status?: number };
