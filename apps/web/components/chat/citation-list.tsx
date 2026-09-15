import type { Citation } from "@/lib/types";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionLabel } from "@/components/ui/section-header";

function citationName(citation: Citation): string {
  const value = citation.source ?? citation.title ?? citation.name;
  return typeof value === "string" ? value : "Knowledge source";
}

export function CitationList({ citations }: { citations: Citation[] }) {
  return <div><SectionLabel>Sources</SectionLabel><div className="space-y-2">{citations.length === 0 ? <EmptyState title="No citations were returned for this answer." /> : citations.map((citation, index) => <div className="flex items-center gap-3 rounded-control border border-line bg-surface-subtle px-4 py-3" key={`${citationName(citation)}-${index}`}><span className="grid size-7 place-items-center rounded-action bg-brand-subtle text-xs font-bold text-brand">{String(index + 1).padStart(2, "0")}</span><span className="text-sm font-medium text-ink-soft">{citationName(citation)}</span></div>)}</div></div>;
}
