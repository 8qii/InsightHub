import type { SalesSummary } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { SectionLabel } from "@/components/ui/section-header";

interface RevenueChartProps {
  values: SalesSummary[];
  formatValue: (value: number | string) => string;
}

export function RevenueChart({ formatValue, values }: RevenueChartProps) {
  const maximum = Math.max(...values.map((item) => Number(item.revenue)), 1);
  const product = values[0]?.product ?? "Revenue";
  const periods = values.map((item) => item.quarter).join(" → ");

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <SectionLabel>Revenue trend</SectionLabel>
          <h2 className="text-lg font-semibold text-ink">{product}</h2>
        </div>
        <Badge tone="brand" compact className="border-0">{periods}</Badge>
      </div>
      <div className="mt-7 flex h-40 items-end gap-8 border-b border-line px-4">
        {values.map((item, index) => (
          <div className="flex h-full flex-1 flex-col items-center justify-end gap-2" key={item.quarter}>
            <div className="text-xs font-semibold text-ink-soft">{formatValue(item.revenue)}</div>
            <div
              className={`w-full max-w-20 rounded-t-control ${index === values.length - 1 ? "bg-brand" : "bg-brand-muted"}`}
              style={{ height: `${Math.max((Number(item.revenue) / maximum) * 100, 8)}%` }}
            />
            <div className="-mb-6 text-xs font-bold text-muted">{item.quarter}</div>
          </div>
        ))}
      </div>
      <p className="mt-9 text-sm leading-6 text-muted">
        Revenue moved from {formatValue(values[0]?.revenue ?? 0)} to {formatValue(values[1]?.revenue ?? 0)} in the selected period.
      </p>
    </Card>
  );
}
