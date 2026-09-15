import type { InvestigationStatus, InvestigationWorkflowState } from "./models";
import { createEmptyWorkflowState, investigationStatuses } from "./workflow";

const STORAGE_KEY = "insighthub.investigation-workflow.v1";

function isStatus(value: unknown): value is InvestigationStatus {
  return typeof value === "string" && investigationStatuses.includes(value as InvestigationStatus);
}

function isTimestamp(value: unknown): value is string {
  return typeof value === "string" && Number.isFinite(Date.parse(value));
}

export function readInvestigationWorkflow(): InvestigationWorkflowState {
  if (typeof window === "undefined") return createEmptyWorkflowState();
  try {
    const value = JSON.parse(window.localStorage.getItem(STORAGE_KEY) ?? "null") as Partial<InvestigationWorkflowState> | null;
    if (!value || value.version !== 1 || !value.records || !Array.isArray(value.interactions)) return createEmptyWorkflowState();
    const records = Object.fromEntries(Object.entries(value.records).filter(([, record]) => (
      record
      && typeof record.investigationId === "string"
      && isStatus(record.status)
      && isTimestamp(record.detectedAt)
      && isTimestamp(record.updatedAt)
      && (record.lastOpenedAt === null || isTimestamp(record.lastOpenedAt))
      && typeof record.openCount === "number"
      && record.snapshot
      && typeof record.snapshot.title === "string"
      && typeof record.snapshot.summary === "string"
      && typeof record.snapshot.metric === "string"
      && ["high", "medium", "low"].includes(record.snapshot.priority)
    )));
    const interactions = value.interactions.filter((interaction) => (
      interaction
      && typeof interaction.id === "string"
      && typeof interaction.investigationId === "string"
      && ["investigation_opened", "analysis_completed", "status_changed"].includes(interaction.type)
      && isTimestamp(interaction.occurredAt)
      && typeof interaction.label === "string"
    ));
    return { version: 1, records, interactions } as InvestigationWorkflowState;
  } catch {
    return createEmptyWorkflowState();
  }
}

export function writeInvestigationWorkflow(state: InvestigationWorkflowState) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // The workflow remains usable in memory when browser storage is unavailable.
  }
}
