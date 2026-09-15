import assert from "node:assert/strict";
import test from "node:test";
import type { Overview } from "@/lib/types";
import {
  createActivityTimeline,
  createEmptyWorkflowState,
  createRecentAnalysisHistory,
  createSignalQueuePresentation,
  recordAnalysisCompleted,
  recordInvestigationOpen,
  syncWorkflowSignals,
  updateInvestigationStatus,
} from "./workflow";

const overview: Overview = {
  period: "FY 2031",
  scope: "Northwind Operations",
  as_of_date: "2031-12-31",
  summary: {
    net_revenue: 1,
    gross_margin: 1,
    gross_margin_rate: 1,
    return_rate: 0,
    inventory_risk_products: 0,
    inventory_risk_units: 0,
  },
  signals: [{
    signal_id: "capacity-variance",
    severity: "medium",
    title: "Capacity variance requires review",
    summary: "Output moved outside the reporting baseline.",
    metric: "8.2% variance",
  }],
  drivers: [],
  evidence: [],
  investigations: [],
};

test("signal queue presentation is generic and starts with a new lifecycle", () => {
  const state = syncWorkflowSignals(createEmptyWorkflowState(), overview);
  const [item] = createSignalQueuePresentation(overview, state);

  assert.equal(item.title, "Capacity variance requires review");
  assert.equal(item.status, "new");
  assert.equal(item.statusLabel, "New");
  assert.equal(item.href, "/dashboard/investigations/capacity-variance");
});

test("opening and completing analysis creates recent local history", () => {
  let state = syncWorkflowSignals(createEmptyWorkflowState(), overview);
  state = recordInvestigationOpen(state, "capacity-variance", "2032-01-02T10:00:00.000Z");
  state = recordInvestigationOpen(state, "capacity-variance", "2032-01-02T10:00:01.000Z");
  state = recordAnalysisCompleted(state, "capacity-variance", "2032-01-02T10:05:00.000Z");

  assert.equal(state.records["capacity-variance"]?.status, "analyzed");
  assert.equal(state.records["capacity-variance"]?.openCount, 1);
  assert.deepEqual(createRecentAnalysisHistory(state).map((item) => item.action), [
    "Analysis completed",
    "Investigation opened",
  ]);
  assert.deepEqual(createActivityTimeline(state.records["capacity-variance"]!, state.interactions).map((item) => item.state), [
    "complete",
    "complete",
    "complete",
    "complete",
  ]);
});

test("resolved and dismissed are supported terminal decisions", () => {
  let state = syncWorkflowSignals(createEmptyWorkflowState(), overview);
  state = updateInvestigationStatus(state, "capacity-variance", "resolved", "2032-01-03T09:00:00.000Z");
  assert.equal(state.records["capacity-variance"]?.status, "resolved");
  assert.equal(createActivityTimeline(state.records["capacity-variance"]!, state.interactions).at(-1)?.title, "Decision resolved");

  state = updateInvestigationStatus(state, "capacity-variance", "dismissed", "2032-01-03T09:10:00.000Z");
  assert.equal(state.records["capacity-variance"]?.status, "dismissed");
  assert.equal(createActivityTimeline(state.records["capacity-variance"]!, state.interactions).at(-1)?.title, "Signal dismissed");
});
