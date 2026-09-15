import { Card } from "@/components/ui/card";
import { SectionLabel } from "@/components/ui/section-header";

type MetricTone = "brand" | "warning";

interface MetricCardProps {
  label: string;
  value: string;
  detail: string;
  tone?: MetricTone;
}

export function MetricCard({ detail, label, tone = "brand", value }: MetricCardProps) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <SectionLabel>{label}</SectionLabel>
        <span className={`size-2 rounded-full ${tone === "warning" ? "bg-warning" : "bg-brand"}`} />
      </div>
      <div className="text-3xl font-semibold tracking-heading text-ink">{value}</div>
      <div className="mt-2 text-sm text-muted">{detail}</div>
    </Card>
  );
}
