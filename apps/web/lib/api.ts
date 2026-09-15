import type {
  AgentResponse,
  AgentRun,
  DiscountViolations,
  InventoryRisk,
  Investigation,
  Overview,
  SalesSummary,
} from "./types";

const browserApiPrefix = "/backend";

function apiPath(path: string): string {
  if (typeof window !== "undefined") return `${browserApiPrefix}${path}`;
  return `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}${path}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 30_000);

  try {
    const response = await fetch(apiPath(path), {
      ...init,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
    const body = (await response.json().catch(() => null)) as
      | { detail?: string; error?: { message?: string } }
      | null;

    if (!response.ok) {
      const error = new Error(body?.detail ?? body?.error?.message ?? `Request failed (${response.status})`) as Error & {
        status?: number;
      };
      error.status = response.status;
      throw error;
    }

    return body as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("The request timed out. Check the API service and try again.");
    }
    if (error instanceof TypeError) {
      throw new Error("InsightHub is unavailable. Check that the API service is running.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

function objectResponse(value: unknown, message: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(message);
  return value as Record<string, unknown>;
}

export async function queryAgent(question: string): Promise<AgentResponse> {
  const value = objectResponse(await request<unknown>("/api/v1/agent/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  }), "The analyst returned an invalid response. Please try again.");
  if (typeof value.answer !== "string" || !Array.isArray(value.sources)) throw new Error("The analyst returned an incomplete response. Please try again.");
  return value as unknown as AgentResponse;
}

export type AgentStreamHandlers = {
  onRun?: (runId: string) => void;
  onToken: (text: string) => void;
  onDone: (sources: AgentResponse["sources"], runId: string) => void;
};

export async function streamAgent(
  question: string,
  handlers: AgentStreamHandlers,
  signal: AbortSignal,
): Promise<void> {
  const response = await fetch(apiPath("/api/v1/agent/query/stream"), {
    method: "POST",
    body: JSON.stringify({ question }),
    signal,
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok || !response.body) {
    throw new Error(`The analyst stream failed (${response.status}).`);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value ?? new Uint8Array(), { stream: !done });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";
    for (const rawEvent of events) {
      const event = parseSseEvent(rawEvent);
      if (event.type === "run") {
        handlers.onRun?.(String(event.data.run_id));
      } else if (event.type === "token") {
        handlers.onToken(String(event.data.text ?? ""));
      } else if (event.type === "done") {
        handlers.onDone((event.data.sources ?? []) as AgentResponse["sources"], String(event.data.run_id));
      } else if (event.type === "error") {
        throw new Error(String(event.data.message ?? "The analyst could not complete this request."));
      }
    }
    if (done) break;
  }
}

function parseSseEvent(raw: string): { type: string; data: Record<string, unknown> } {
  const type = raw.match(/^event: (.+)$/m)?.[1] ?? "message";
  const data = raw.match(/^data: (.+)$/m)?.[1] ?? "{}";
  return { type, data: JSON.parse(data) as Record<string, unknown> };
}

export async function getAgentRun(runId: string): Promise<AgentRun> {
  const value = objectResponse(await request<unknown>(`/api/v1/agent/runs/${encodeURIComponent(runId)}`), "The trace API returned an invalid response.");
  if (typeof value.run_id !== "string" || typeof value.duration_ms !== "number" || !Array.isArray(value.tools)) throw new Error("The trace API returned an incomplete response.");
  return value as unknown as AgentRun;
}

export async function getSalesSummary(product: string, quarter: string): Promise<SalesSummary> {
  const value = objectResponse(await request<unknown>(
    `/api/v1/data/sales/summary?product_name=${encodeURIComponent(product)}&quarter=${quarter}`,
  ), "The sales API returned an invalid response.");
  if (typeof value.product !== "string" || typeof value.quarter !== "string" || value.revenue === undefined || typeof value.order_count !== "number") throw new Error("The sales API returned an incomplete response.");
  return value as unknown as SalesSummary;
}

export async function getInventoryRisk(ageThresholdDays = 90): Promise<InventoryRisk[]> {
  const value = await request<unknown>(
    `/api/v1/data/inventory/risk?age_threshold_days=${ageThresholdDays}`,
  );
  if (!Array.isArray(value)) throw new Error("The inventory API returned an invalid response.");
  return value as InventoryRisk[];
}

export async function getDiscountViolations(): Promise<DiscountViolations> {
  const value = objectResponse(await request<unknown>("/api/v1/data/discount/violations"), "The discount API returned an invalid response.");
  if (typeof value.total_violations !== "number" || typeof value.unapproved_violations !== "number") throw new Error("The discount API returned an incomplete response.");
  return value as unknown as DiscountViolations;
}

function isNumberValue(value: unknown): value is number | string {
  return typeof value === "number" || (typeof value === "string" && value.trim() !== "" && Number.isFinite(Number(value)));
}

function hasStringFields(value: unknown, fields: string[]): value is Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const record = value as Record<string, unknown>;
  return fields.every((field) => typeof record[field] === "string");
}

function fieldIsOneOf(value: unknown, field: string, allowed: string[]): boolean {
  return Boolean(value && typeof value === "object" && !Array.isArray(value) && allowed.includes(String((value as Record<string, unknown>)[field])));
}

function isDateString(value: unknown): value is string {
  return typeof value === "string"
    && /^\d{4}-\d{2}-\d{2}$/.test(value)
    && !Number.isNaN(Date.parse(`${value}T00:00:00Z`));
}

export async function getOverview(): Promise<Overview> {
  const value = objectResponse(await request<unknown>("/api/v1/overview"), "The overview API returned an invalid response.");
  const summary = value.summary && typeof value.summary === "object" && !Array.isArray(value.summary)
    ? value.summary as Record<string, unknown>
    : null;
  if (
    typeof value.period !== "string"
    || typeof value.scope !== "string"
    || !isDateString(value.as_of_date)
    || !summary
    || !isNumberValue(summary.net_revenue)
    || !isNumberValue(summary.gross_margin)
    || !isNumberValue(summary.gross_margin_rate)
    || !isNumberValue(summary.return_rate)
    || typeof summary.inventory_risk_products !== "number"
    || typeof summary.inventory_risk_units !== "number"
    || !Array.isArray(value.signals) || !value.signals.every((item) => hasStringFields(item, ["signal_id", "severity", "title", "summary", "metric"]) && fieldIsOneOf(item, "severity", ["high", "medium", "low"]))
    || !Array.isArray(value.drivers) || !value.drivers.every((item) => hasStringFields(item, ["driver", "status", "summary", "metric"]) && fieldIsOneOf(item, "driver", ["Sales", "Returns", "Discounts", "Inventory"]) && fieldIsOneOf(item, "status", ["positive", "watch", "risk"]))
    || !Array.isArray(value.evidence) || !value.evidence.every((item) => hasStringFields(item, ["source_type", "role", "title", "detail"]) && fieldIsOneOf(item, "source_type", ["document", "database", "metric"]) && fieldIsOneOf(item, "role", ["supporting_context", "metric_source"]))
    || !Array.isArray(value.investigations) || !value.investigations.every((item) => hasStringFields(item, ["question", "rationale"]))
  ) throw new Error("The overview API returned an incomplete response.");
  return value as unknown as Overview;
}

export async function getInvestigation(investigationId: string): Promise<Investigation> {
  const value = objectResponse(await request<unknown>(`/api/v1/investigations/${encodeURIComponent(investigationId)}`), "The investigation API returned an invalid response.");
  if (
    typeof value.investigation_id !== "string"
    || typeof value.title !== "string"
    || typeof value.period !== "string"
    || !isDateString(value.as_of_date)
    || typeof value.executive_summary !== "string"
    || typeof value.conclusion !== "string"
    || typeof value.impact !== "string"
    || !Array.isArray(value.findings) || !value.findings.every((item) => hasStringFields(item, ["title", "summary", "metric", "severity"]) && fieldIsOneOf(item, "severity", ["high", "medium", "low"]))
    || !Array.isArray(value.drivers) || !value.drivers.every((item) => hasStringFields(item, ["area", "status", "summary", "metric"]) && fieldIsOneOf(item, "area", ["Demand", "Returns", "Inventory", "Business context"]) && fieldIsOneOf(item, "status", ["positive", "watch", "risk"]))
    || !Array.isArray(value.evidence) || !value.evidence.every((item) => hasStringFields(item, ["observed_on", "source_type", "role", "title", "detail"]) && isDateString((item as Record<string, unknown>).observed_on) && fieldIsOneOf(item, "source_type", ["document", "database", "metric"]) && fieldIsOneOf(item, "role", ["supporting_context", "metric_source"]))
    || !Array.isArray(value.suggested_questions) || !value.suggested_questions.every((item) => hasStringFields(item, ["question", "rationale"]))
  ) throw new Error("The investigation API returned an incomplete response.");
  return value as unknown as Investigation;
}
