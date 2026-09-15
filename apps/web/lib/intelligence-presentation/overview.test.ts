import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createOverviewPresentation } from "./overview";
import type { Overview } from "@/lib/types";

const arbitraryOverview: Overview = {
  period: "FY 2028 H1",
  scope: "Atlas Manufacturing",
  as_of_date: "2028-06-30",
  summary: {
    net_revenue: "8600000",
    gross_margin: "3100000",
    gross_margin_rate: "0.36",
    return_rate: "0.04",
    inventory_risk_products: 18,
    inventory_risk_units: 7400,
  },
  signals: [
    {
      signal_id: "orion-demand-variance",
      severity: "high",
      title: "Product Orion demand variance",
      summary: "Demand closed below the prior reporting baseline.",
      metric: "16.0% variance",
    },
  ],
  drivers: [],
  evidence: [
    {
      source_type: "database",
      role: "metric_source",
      title: "Order performance",
      detail: "Reporting-period revenue and unit demand.",
    },
  ],
  investigations: [],
};

test("presentation supports arbitrary company scope and insight title", () => {
  const presentation = createOverviewPresentation(arbitraryOverview);

  assert.equal(presentation.company, "Atlas Manufacturing");
  assert.equal(presentation.scope, "Atlas Manufacturing");
  assert.equal(presentation.preparationStatus, "Analyst briefing prepared");
  assert.equal(presentation.insight?.headline, "Product Orion demand variance");
  assert.equal(presentation.insight?.observation, "Demand closed below the prior reporting baseline.");
  assert.equal(presentation.insight?.impact, "16.0% variance");
  assert.equal(presentation.insight?.evidenceSummary, "1 source prepared for review.");
  assert.equal(presentation.attention[0]?.actionHref, "/dashboard/investigations/orion-demand-variance");
});

test("presentation is empty-safe when an overview has no signals", () => {
  const presentation = createOverviewPresentation({
    ...arbitraryOverview,
    signals: [],
    evidence: [],
  });

  assert.equal(presentation.insight, null);
  assert.equal(presentation.preparationStatus, "No executive signals prepared");
  assert.equal(presentation.evidenceRelationship.finding, "No executive finding is available");
});

test("rendering components do not embed the demo product name", () => {
  const componentFiles = [
    new URL("../../components/dashboard/dashboard-view.tsx", import.meta.url),
    new URL("../../components/layout/top-context-bar.tsx", import.meta.url),
    new URL("../../components/chat/analyst-chat.tsx", import.meta.url),
    new URL("../../components/intelligence/investigation-view.tsx", import.meta.url),
    new URL("../../components/signals/signals-view.tsx", import.meta.url),
  ];

  for (const file of componentFiles) {
    assert.equal(readFileSync(file, "utf8").includes("Product Luna"), false);
  }
});
