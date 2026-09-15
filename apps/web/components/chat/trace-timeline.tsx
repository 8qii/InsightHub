import type { AgentRun } from "@/lib/types";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionLabel } from "@/components/ui/section-header";

export function TraceTimeline({ trace }: { trace: AgentRun }) {
  return <div><SectionLabel>Agent trace</SectionLabel><div className="mb-4 flex items-center justify-between text-xs text-muted"><span>{trace.status}</span><span>{Math.round(trace.duration_ms)} ms total</span></div>{trace.tools.length === 0 ? <EmptyState title="No tools were needed for this answer." /> : <div className="relative space-y-4 pl-5 before:absolute before:bottom-2 before:left-[5px] before:top-2 before:w-px before:bg-brand-border">{trace.tools.map((tool, index) => <div className="relative" key={`${tool.name}-${index}`}><span className="absolute -left-5 top-1 size-[11px] rounded-full border-2 border-white bg-brand ring-1 ring-brand" /><div className="text-sm font-semibold text-ink-soft">{tool.name}</div><div className="mt-1 text-xs text-muted">{tool.status} · {Math.round(tool.duration_ms)} ms</div></div>)}</div>}</div>;
}
