import type { PrioritySignal } from "@/lib/types";

export type InvestigationStatus = "new" | "reviewing" | "analyzed" | "resolved" | "dismissed";

export type InvestigationSnapshot = {
  title: string;
  summary: string;
  metric: string;
  priority: PrioritySignal["severity"];
};

export type InvestigationWorkflowRecord = {
  investigationId: string;
  status: InvestigationStatus;
  detectedAt: string;
  updatedAt: string;
  lastOpenedAt: string | null;
  openCount: number;
  snapshot: InvestigationSnapshot;
};

export type InvestigationInteractionType = "investigation_opened" | "analysis_completed" | "status_changed";

export type InvestigationInteraction = {
  id: string;
  investigationId: string;
  type: InvestigationInteractionType;
  occurredAt: string;
  label: string;
};

export type InvestigationWorkflowState = {
  version: 1;
  records: Record<string, InvestigationWorkflowRecord>;
  interactions: InvestigationInteraction[];
};

export type ActivityTimelineItemPresentation = {
  id: string;
  title: string;
  detail: string;
  state: "complete" | "current" | "upcoming";
  occurredAt: string | null;
};

export type SignalQueueItemPresentation = InvestigationSnapshot & {
  id: string;
  status: InvestigationStatus;
  statusLabel: string;
  updatedAt: string;
  href: string;
};

export type AnalysisHistoryItemPresentation = {
  id: string;
  investigationId: string;
  title: string;
  action: string;
  occurredAt: string;
  href: string;
};
