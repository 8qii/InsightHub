import type { InvestigationEvidence } from "@/lib/types";
import { Card } from "@/components/ui/card";

const sourceLabels = { document: "Document context", database: "Database metric", metric: "Snapshot metric" };
const roleLabels = { supporting_context: "Supporting context", metric_source: "Calculated input" };
const sourceStyles = {
  document: "bg-warning",
  database: "bg-brand",
  metric: "bg-ink-soft",
};

function displayDate(value: string) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" }).format(new Date(`${value}T00:00:00Z`));
}

export function EvidenceTimeline({ evidence }: { evidence: InvestigationEvidence[] }) {
  return (
    <div className="space-y-4">
      {evidence.map((item) => <div className="grid gap-3 sm:grid-cols-[120px_1fr]" key={`${item.observed_on}-${item.title}`}>
        <div className="pt-4 text-xs font-bold uppercase tracking-eyebrow text-muted">{displayDate(item.observed_on)}</div>
        <Card tone="utility" className={`relative border-l-4 p-5 ${item.source_type === "document" ? "border-l-warning" : item.source_type === "database" ? "border-l-brand" : "border-l-ink-soft"}`}>
          <span className={`absolute -left-[1.7rem] top-6 size-2 rounded-full ring-4 ring-canvas ${sourceStyles[item.source_type]}`} />
          <div className="flex flex-wrap gap-x-3 gap-y-1 text-[10px] font-bold uppercase tracking-eyebrow text-muted"><span>{sourceLabels[item.source_type]}</span><span>{roleLabels[item.role]}</span></div>
          <h3 className="mt-3 text-base font-semibold text-ink">{item.title}</h3>
          <p className="mt-2 text-sm leading-6 text-muted">{item.detail}</p>
        </Card>
      </div>)}
    </div>
  );
}
