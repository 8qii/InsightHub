import type { DiscountViolations } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { SectionLabel } from "@/components/ui/section-header";

export function DiscountChart({ values }: { values: DiscountViolations }) {
  const maximum = Math.max(values.total_violations, 1);
  const bars = [
    { label: "Total violations", value: values.total_violations, className: "bg-warning" },
    { label: "Unapproved", value: values.unapproved_violations, className: "bg-warning-muted" },
  ];

  return (
    <Card className="p-6">
      <SectionLabel>Discount controls</SectionLabel>
      <h2 className="text-lg font-semibold text-ink">Policy violations</h2>
      <div className="mt-7 space-y-5">
        {bars.map((bar) => (
          <div key={bar.label}>
            <div className="mb-2 flex justify-between text-sm">
              <span className="text-muted">{bar.label}</span>
              <strong>{bar.value}</strong>
            </div>
            <div className="h-3 rounded-full bg-surface-muted">
              <div className={`h-3 rounded-full ${bar.className}`} style={{ width: `${(bar.value / maximum) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
      <p className="mt-7 text-sm leading-6 text-muted">Unapproved violations represent cases requiring commercial review.</p>
    </Card>
  );
}
