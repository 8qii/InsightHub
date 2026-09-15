import { Card } from "@/components/ui/card";
import { SectionLabel } from "@/components/ui/section-header";

type MetricTone = "brand" | "warning";

interface MetricCardProps {
  label: string;
  value: string;
  detail: string;
  interpretation?: string;
  tone?: MetricTone;
}

export function MetricCard({ detail, interpretation, label, tone = "brand", value }: MetricCardProps) {
  return (
    <Card tone="utility" className="p-5">
      <div className="flex items-start justify-between gap-4">
        <SectionLabel>{label}</SectionLabel>
        {interpretation ? <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-eyebrow ${tone === "warning" ? "bg-warning-soft text-warning-strong" : "bg-brand-soft text-brand"}`}>{interpretation}</span> : null}
      </div>
      <div className="mt-1 text-2xl font-semibold tracking-heading text-ink">{value}</div>
      <div className="mt-2 text-sm leading-5 text-muted">{detail}</div>
    </Card>
  );
}
