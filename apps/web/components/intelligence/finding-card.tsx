import type { InvestigationFinding } from "@/lib/types";
import { Card } from "@/components/ui/card";

const severityStyles = {
  high: { border: "border-l-danger", badge: "border-danger-border bg-danger-soft text-danger" },
  medium: { border: "border-l-warning", badge: "border-warning-border bg-warning-soft text-warning-strong" },
  low: { border: "border-l-brand", badge: "border-brand-border bg-brand-soft text-brand" },
};

export function FindingCard({ finding }: { finding: InvestigationFinding }) {
  const severity = severityStyles[finding.severity];
  return (
    <Card tone="editorial" className={`border-l-4 p-5 sm:p-6 ${severity.border}`}>
      <div className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-eyebrow ${severity.badge}`}>{finding.severity} priority</div>
      <h3 className="mt-5 text-lg font-semibold tracking-heading text-ink">{finding.title}</h3>
      <p className="mt-2 text-sm leading-6 text-muted">{finding.summary}</p>
      <div className="mt-5 rounded-control bg-surface-subtle px-3 py-2.5 text-sm font-bold text-ink">{finding.metric}</div>
    </Card>
  );
}
