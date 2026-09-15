import type { EvidencePreview } from "@/lib/types";

export type InsightPresentation = {
  headline: string;
  observation: string;
  summary: string;
  impact: string;
  recommendation: string;
  recommendationHref: string;
  confidence: string;
  evidenceCount: number;
  evidenceSummary: string;
  priority: "high" | "medium" | "low";
};

export type AttentionItemPresentation = {
  id: string;
  severity: "high" | "medium" | "low";
  title: string;
  observation: string;
  impact: string;
  action: string;
  actionHref: string;
  evidenceCount: number;
};

export type EvidenceRelationshipPresentation = {
  finding: string;
  supportingEvidence: Array<{
    id: string;
    sourceType: EvidencePreview["source_type"];
    sourceLabel: string;
    roleLabel: string;
    title: string;
    detail: string;
  }>;
};

export type OverviewPresentation = {
  company: string;
  period: string;
  scope: string;
  asOfDate: string;
  evidenceCount: number;
  preparationStatus: string;
  insight: InsightPresentation | null;
  attention: AttentionItemPresentation[];
  evidenceRelationship: EvidenceRelationshipPresentation;
  metrics: Array<{ label: string; value: string; detail: string }>;
};
