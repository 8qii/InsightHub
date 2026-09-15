import Link from "next/link";
import type { SuggestedQuestion } from "@/lib/types";
import { Card } from "@/components/ui/card";

export function QuestionSuggestion({ index, suggestion }: { index: number; suggestion: SuggestedQuestion }) {
  return (
    <Card className="group flex h-full flex-col p-5 transition hover:-translate-y-0.5 hover:border-brand-border hover:shadow-editorial focus-within:border-brand-border sm:p-6">
      <div className="text-label font-bold uppercase tracking-label text-brand">Next question {String(index).padStart(2, "0")}</div>
      <h3 className="mt-5 text-lg font-semibold leading-6 tracking-heading text-ink">{suggestion.question}</h3>
      <p className="mt-2 flex-1 text-sm leading-6 text-muted">{suggestion.rationale}</p>
      <Link href="/" className="mt-6 inline-flex items-center justify-between rounded-control border border-brand-border bg-brand-soft px-4 py-3 text-sm font-bold text-brand transition hover:bg-brand-subtle focus-visible:outline-none focus-visible:shadow-focus"><span>Ask in Analyst</span><span aria-hidden="true" className="transition-transform group-hover:translate-x-0.5">-&gt;</span></Link>
    </Card>
  );
}
