import type { InvestigationStatus } from "@/lib/investigation-workflow";
import { investigationStatusLabels } from "@/lib/investigation-workflow";

const statusStyles: Record<InvestigationStatus, string> = {
  new: "border-line-strong bg-surface-muted text-ink-soft",
  reviewing: "border-warning-border bg-warning-soft text-warning-strong",
  analyzed: "border-brand-border bg-brand-soft text-brand",
  resolved: "border-brand bg-brand text-white",
  dismissed: "border-line bg-surface-subtle text-muted",
};

export function InvestigationStatusIndicator({ status }: { status: InvestigationStatus }) {
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-eyebrow ${statusStyles[status]}`}>{investigationStatusLabels[status]}</span>;
}
