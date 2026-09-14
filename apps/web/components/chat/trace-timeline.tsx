import type { AgentRun } from "@/lib/types";
import { SectionLabel } from "@/components/ui";

export function TraceTimeline({ trace }: { trace: AgentRun }) {
  return <div><SectionLabel>Agent trace</SectionLabel><div className="mb-4 flex items-center justify-between text-xs text-[#687684]"><span>{trace.status}</span><span>{Math.round(trace.duration_ms)} ms total</span></div>{trace.tools.length === 0 ? <div className="rounded-xl border border-dashed border-[#dbe2e7] p-4 text-sm text-[#687684]">No tools were needed for this answer.</div> : <div className="relative space-y-4 pl-5 before:absolute before:bottom-2 before:left-[5px] before:top-2 before:w-px before:bg-[#bfe0dc]">{trace.tools.map((tool, index) => <div className="relative" key={`${tool.name}-${index}`}><span className="absolute -left-5 top-1 size-[11px] rounded-full border-2 border-white bg-[#087f7b] ring-1 ring-[#087f7b]" /><div className="text-sm font-semibold text-[#31414c]">{tool.name}</div><div className="mt-1 text-xs text-[#687684]">{tool.status} · {Math.round(tool.duration_ms)} ms</div></div>)}</div>}</div>;
}
