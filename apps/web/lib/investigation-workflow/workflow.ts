import type { Overview, PrioritySignal } from "@/lib/types";
import type {
  ActivityTimelineItemPresentation,
  AnalysisHistoryItemPresentation,
  InvestigationInteraction,
  InvestigationSnapshot,
  InvestigationStatus,
  InvestigationWorkflowRecord,
  InvestigationWorkflowState,
  SignalQueueItemPresentation,
} from "./models";

export const investigationStatuses: InvestigationStatus[] = ["new", "reviewing", "analyzed", "resolved", "dismissed"];

export const investigationStatusLabels: Record<InvestigationStatus, string> = {
  new: "New",
  reviewing: "Reviewing",
  analyzed: "Analyzed",
  resolved: "Resolved",
  dismissed: "Dismissed",
};

export function createEmptyWorkflowState(): InvestigationWorkflowState {
  return { version: 1, records: {}, interactions: [] };
}

function snapshot(signal: PrioritySignal) {
  return {
    title: signal.title,
    summary: signal.summary,
    metric: signal.metric,
    priority: signal.severity,
  };
}

export function syncWorkflowSignals(
  state: InvestigationWorkflowState,
  overview: Overview,
): InvestigationWorkflowState {
  const records = { ...state.records };
  for (const signal of overview.signals) {
    const existing = records[signal.signal_id];
    records[signal.signal_id] = existing
      ? { ...existing, snapshot: snapshot(signal) }
      : {
          investigationId: signal.signal_id,
          status: "new",
          detectedAt: `${overview.as_of_date}T00:00:00.000Z`,
          updatedAt: `${overview.as_of_date}T00:00:00.000Z`,
          lastOpenedAt: null,
          openCount: 0,
          snapshot: snapshot(signal),
        };
  }
  return { ...state, records };
}

export function ensureInvestigationRecord(
  state: InvestigationWorkflowState,
  investigationId: string,
  investigationSnapshot: InvestigationSnapshot,
  detectedAt: string,
): InvestigationWorkflowState {
  if (state.records[investigationId]) return state;
  return {
    ...state,
    records: {
      ...state.records,
      [investigationId]: {
        investigationId,
        status: "new",
        detectedAt,
        updatedAt: detectedAt,
        lastOpenedAt: null,
        openCount: 0,
        snapshot: investigationSnapshot,
      },
    },
  };
}

function addInteraction(
  state: InvestigationWorkflowState,
  interaction: Omit<InvestigationInteraction, "id">,
): InvestigationWorkflowState {
  const previous = state.interactions[0];
  if (
    previous?.investigationId === interaction.investigationId
    && previous.type === interaction.type
    && Math.abs(Date.parse(previous.occurredAt) - Date.parse(interaction.occurredAt)) < 5_000
  ) return state;

  return {
    ...state,
    interactions: [
      { ...interaction, id: `${interaction.investigationId}-${interaction.type}-${interaction.occurredAt}` },
      ...state.interactions,
    ].slice(0, 100),
  };
}

export function recordInvestigationOpen(
  state: InvestigationWorkflowState,
  investigationId: string,
  occurredAt: string,
): InvestigationWorkflowState {
  const record = state.records[investigationId];
  if (!record) return state;
  const previous = state.interactions[0];
  if (
    previous?.investigationId === investigationId
    && previous.type === "investigation_opened"
    && Math.abs(Date.parse(previous.occurredAt) - Date.parse(occurredAt)) < 5_000
  ) return state;
  const nextStatus = record.status === "new" ? "reviewing" : record.status;
  const withRecord = {
    ...state,
    records: {
      ...state.records,
      [investigationId]: {
        ...record,
        status: nextStatus,
        updatedAt: occurredAt,
        lastOpenedAt: occurredAt,
        openCount: record.openCount + 1,
      },
    },
  };
  return addInteraction(withRecord, {
    investigationId,
    type: "investigation_opened",
    occurredAt,
    label: "Investigation opened",
  });
}

export function recordAnalysisCompleted(
  state: InvestigationWorkflowState,
  investigationId: string,
  occurredAt: string,
): InvestigationWorkflowState {
  const record = state.records[investigationId];
  if (!record || record.status === "resolved" || record.status === "dismissed") return state;
  const withRecord = {
    ...state,
    records: {
      ...state.records,
      [investigationId]: { ...record, status: "analyzed" as const, updatedAt: occurredAt },
    },
  };
  return addInteraction(withRecord, {
    investigationId,
    type: "analysis_completed",
    occurredAt,
    label: "Analysis completed",
  });
}

export function updateInvestigationStatus(
  state: InvestigationWorkflowState,
  investigationId: string,
  status: InvestigationStatus,
  occurredAt: string,
): InvestigationWorkflowState {
  const record = state.records[investigationId];
  if (!record || record.status === status) return state;
  const withRecord = {
    ...state,
    records: {
      ...state.records,
      [investigationId]: { ...record, status, updatedAt: occurredAt },
    },
  };
  return addInteraction(withRecord, {
    investigationId,
    type: "status_changed",
    occurredAt,
    label: `Status changed to ${investigationStatusLabels[status]}`,
  });
}

export function createSignalQueuePresentation(
  overview: Overview,
  state: InvestigationWorkflowState,
): SignalQueueItemPresentation[] {
  return overview.signals.map((signal) => {
    const record = state.records[signal.signal_id];
    const status = record?.status ?? "new";
    return {
      id: signal.signal_id,
      ...snapshot(signal),
      status,
      statusLabel: investigationStatusLabels[status],
      updatedAt: record?.updatedAt ?? `${overview.as_of_date}T00:00:00.000Z`,
      href: `/dashboard/investigations/${encodeURIComponent(signal.signal_id)}`,
    };
  });
}

export function createActivityTimeline(
  record: InvestigationWorkflowRecord,
  interactions: InvestigationInteraction[],
): ActivityTimelineItemPresentation[] {
  const completedAt = interactions.find((item) => item.investigationId === record.investigationId && item.type === "analysis_completed")?.occurredAt ?? null;
  const reviewing = record.status !== "new";
  const analyzed = record.status === "analyzed" || record.status === "resolved" || completedAt !== null;
  const terminal = record.status === "resolved" || record.status === "dismissed";
  const items: ActivityTimelineItemPresentation[] = [
    { id: "detected", title: "Signal detected", detail: "The signal entered the intelligence queue.", state: "complete", occurredAt: record.detectedAt },
    { id: "evidence", title: "Evidence collected", detail: "Available evidence was prepared for analyst review.", state: analyzed ? "complete" : reviewing ? "current" : "upcoming", occurredAt: completedAt },
    { id: "analysis", title: "Analysis completed", detail: "The curated analysis was reviewed in the workspace.", state: analyzed ? "complete" : "upcoming", occurredAt: completedAt },
    { id: "recommendation", title: "Recommendation prepared", detail: "The finding is ready for a tracked decision.", state: analyzed ? "complete" : "upcoming", occurredAt: completedAt },
  ];
  if (terminal) {
    items.push({
      id: "decision",
      title: record.status === "resolved" ? "Decision resolved" : "Signal dismissed",
      detail: record.status === "resolved" ? "The investigation was closed with a resolution." : "The signal was closed without further action.",
      state: "complete",
      occurredAt: record.updatedAt,
    });
  }
  return items;
}

export function createRecentAnalysisHistory(
  state: InvestigationWorkflowState,
  limit = 6,
): AnalysisHistoryItemPresentation[] {
  return state.interactions.slice(0, limit).flatMap((interaction) => {
    const record = state.records[interaction.investigationId];
    if (!record) return [];
    return [{
      id: interaction.id,
      investigationId: interaction.investigationId,
      title: record.snapshot.title,
      action: interaction.label,
      occurredAt: interaction.occurredAt,
      href: `/dashboard/investigations/${encodeURIComponent(interaction.investigationId)}`,
    }];
  });
}
