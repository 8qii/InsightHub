import type { Citation } from "@/lib/types";
import { SectionLabel } from "@/components/ui";

function citationName(citation: Citation): string {
  const value = citation.source ?? citation.title ?? citation.name;
  return typeof value === "string" ? value : "Knowledge source";
}

export function CitationList({ citations }: { citations: Citation[] }) {
  return <div><SectionLabel>Sources</SectionLabel><div className="space-y-2">{citations.length === 0 ? <div className="rounded-xl border border-dashed border-[#dbe2e7] p-4 text-sm text-[#687684]">No citations were returned for this answer.</div> : citations.map((citation, index) => <div className="flex items-center gap-3 rounded-xl border border-[#dbe2e7] bg-[#fbfcfc] px-4 py-3" key={`${citationName(citation)}-${index}`}><span className="grid size-7 place-items-center rounded-lg bg-[#e4f2f0] text-xs font-bold text-[#087f7b]">{String(index + 1).padStart(2, "0")}</span><span className="text-sm font-medium text-[#31414c]">{citationName(citation)}</span></div>)}</div></div>;
}
