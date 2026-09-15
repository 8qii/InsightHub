import type { BusinessDriver } from "@/lib/types";
import { Card } from "@/components/ui/card";

const statusStyles = {
  positive: { dot: "bg-brand", pill: "border-brand-border bg-brand-soft text-brand" },
  watch: { dot: "bg-warning", pill: "border-warning-border bg-warning-soft text-warning-strong" },
  risk: { dot: "bg-danger", pill: "border-danger-border bg-danger-soft text-danger" },
};

export function DriverAnalysis({ drivers }: { drivers: BusinessDriver[] }) {
  return (
    <Card tone="utility" className="overflow-hidden p-2 sm:p-3">
      <div className="space-y-2">
        {drivers.map((driver) => (
          <div className="grid gap-4 rounded-control border border-transparent bg-surface px-4 py-5 transition hover:border-line-strong sm:grid-cols-[150px_1fr_190px] sm:items-center sm:px-5" key={driver.driver}>
            <div className="text-sm font-semibold text-ink">
              <div className="flex items-center gap-3"><span className={`size-2 rounded-full ${statusStyles[driver.status].dot}`} />{driver.driver}</div>
              <div className={`mt-2 ml-5 inline-flex rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-eyebrow ${statusStyles[driver.status].pill}`}>{driver.status}</div>
            </div>
            <p className="text-sm leading-6 text-muted">{driver.summary}</p>
            <div className="rounded-control bg-surface-subtle px-3 py-2.5 text-sm font-bold text-ink sm:text-right">{driver.metric}</div>
          </div>
        ))}
      </div>
    </Card>
  );
}
