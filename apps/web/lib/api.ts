import type {
  AgentResponse,
  DiscountViolations,
  InventoryRisk,
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
      | { detail?: string }
      | null;

    if (!response.ok) {
      const error = new Error(body?.detail ?? `Request failed (${response.status})`) as Error & {
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
