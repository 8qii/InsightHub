import type { InsightPresentation } from "@/lib/intelligence-presentation";

const priorityStyles = {
  high: "border-danger-border bg-danger-soft text-danger",
  medium: "border-warning-border bg-warning-soft text-warning-strong",
  low: "border-brand-border bg-brand-soft text-brand",
};

export function ConfidenceIndicator({ insight }: { insight: InsightPresentation }) {
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-eyebrow ${priorityStyles[insight.priority]}`}>{insight.confidence}</span>;
}
