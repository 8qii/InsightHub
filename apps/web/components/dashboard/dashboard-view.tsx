"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { DiscountChart } from "@/components/charts/discount-chart";
import { RevenueChart } from "@/components/charts/revenue-chart";
import { MetricCard } from "@/components/intelligence/metric-card";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionLabel } from "@/components/ui/section-header";
import { Spinner } from "@/components/ui/spinner";
import { getDiscountViolations, getInventoryRisk, getSalesSummary } from "@/lib/api";
import type { DiscountViolations, InventoryRisk, SalesSummary } from "@/lib/types";

function money(value: number | string) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(Number(value));
}

export function DashboardView() {
  const [sales, setSales] = useState<SalesSummary | null>(null);
  const [trend, setTrend] = useState<SalesSummary[]>([]);
  const [inventory, setInventory] = useState<InventoryRisk[] | null>(null);
  const [discounts, setDiscounts] = useState<DiscountViolations | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getSalesSummary("Product Luna", "Q3"),
      getSalesSummary("Product Luna", "Q2"),
      getInventoryRisk(90),
      getDiscountViolations(),
    ])
      .then(([q3, q2, inventoryData, discountData]) => {
        setSales(q3);
        setTrend([q2, q3]);
        setInventory(inventoryData);
        setDiscounts(discountData);
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Dashboard data is unavailable."))
      .finally(() => setLoading(false));
  }, []);

  const oldest = inventory?.reduce((max, item) => Math.max(max, item.age_days), 0) ?? 0;

  return (
    <AppShell page="Overview" scope="Product Luna">
      <main className="w-full">
        <div className="mb-8 flex flex-col justify-between gap-5 border-b border-line pb-6 sm:flex-row sm:items-end">
          <div>
            <div className="mb-3 text-label font-bold uppercase tracking-label text-brand">Executive overview · Q3</div>
            <h1 className="text-4xl font-semibold tracking-heading text-ink">Business pulse</h1>
            <p className="mt-3 text-muted">A concise view of the metrics currently available to InsightHub.</p>
          </div>
          <div className="rounded-control border border-line bg-surface px-4 py-3 text-sm text-muted">
            Scope: <strong className="text-ink">Product Luna · Q2 / Q3</strong>
          </div>
        </div>

        {loading ? <div className="mb-6 flex items-center gap-3 rounded-control border border-brand-border bg-brand-soft p-4 text-sm text-brand"><Spinner /> Loading live business data...</div> : null}
        {error ? <div role="alert" className="mb-6 rounded-control border border-danger-border bg-danger-soft p-4 text-sm text-danger">{error}</div> : null}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Q3 revenue" value={sales ? money(sales.revenue) : "—"} detail={sales ? `${sales.product} · ${sales.quarter}` : "Awaiting sales API"} />
          <MetricCard label="Orders" value={sales ? sales.order_count.toLocaleString() : "—"} detail="Recorded in selected period" />
          <MetricCard label="Risky products" value={inventory ? inventory.length.toLocaleString() : "—"} detail="Inventory older than 90 days" tone="warning" />
          <MetricCard label="Policy violations" value={discounts ? discounts.total_violations.toLocaleString() : "—"} detail={discounts ? `${discounts.unapproved_violations} unapproved` : "Awaiting policy API"} tone="warning" />
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          {trend.length === 2 ? <RevenueChart values={trend} formatValue={money} /> : null}
          {discounts ? <DiscountChart values={discounts} /> : null}
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_.8fr]">
          <Card className="p-6">
            <SectionLabel>Inventory watchlist</SectionLabel>
            {inventory?.length ? (
              <div className="divide-y divide-line">
                {inventory.map((item) => (
                  <div className="flex items-center justify-between gap-4 py-4" key={item.product}>
                    <div>
                      <div className="font-semibold text-ink-soft">{item.product}</div>
                      <div className="mt-1 text-sm text-muted">{item.stock_quantity.toLocaleString()} units in stock</div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-warning-strong">{item.age_days}</div>
                      <div className="text-label font-bold uppercase tracking-label text-muted">age</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : <EmptyState title="No aging inventory returned." />}
          </Card>

          <Card className="p-6">
            <SectionLabel>Signal notes</SectionLabel>
            <div className="space-y-5">
              <div>
                <div className="text-sm font-semibold text-ink">Oldest inventory</div>
                <div className="mt-1 text-3xl font-semibold text-warning-strong">{oldest || "—"}<span className="ml-1 text-base font-normal text-muted">days</span></div>
              </div>
              <div className="border-t border-surface-muted pt-5 text-sm leading-6 text-muted">Use the analyst to connect these operational signals with policy and company knowledge.</div>
              <Link href="/" className="inline-block text-sm font-bold text-brand">Open a cross-source question →</Link>
            </div>
          </Card>
        </div>
      </main>
    </AppShell>
  );
}
