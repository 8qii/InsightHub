import Link from "next/link";
import type { SuggestedInvestigation } from "@/lib/types";
import { Card } from "@/components/ui/card";

export function InvestigationCard({ index, investigation }: { index: number; investigation: SuggestedInvestigation }) {
  return (
    <Card className="group relative flex h-full flex-col overflow-hidden p-5 transition hover:-translate-y-0.5 hover:border-brand-border hover:shadow-editorial focus-within:border-brand-border sm:p-6">
      <div className="absolute right-4 top-3 text-5xl font-semibold tracking-heading text-surface-muted">{String(index).padStart(2, "0")}</div>
      <div className="relative text-label font-bold uppercase tracking-label text-brand">Investigation pathway</div>
      <h3 className="relative mt-6 max-w-[90%] text-lg font-semibold leading-6 tracking-heading text-ink">{investigation.question}</h3>
      <p className="mt-2 flex-1 text-sm leading-6 text-muted">{investigation.rationale}</p>
      <Link href="/" className="mt-6 inline-flex items-center justify-between rounded-control border border-brand-border bg-brand-soft px-4 py-3 text-sm font-bold text-brand transition hover:bg-brand-subtle focus-visible:outline-none focus-visible:shadow-focus"><span>Open in Analyst</span><span aria-hidden="true" className="transition-transform group-hover:translate-x-0.5">-&gt;</span></Link>
    </Card>
  );
}
