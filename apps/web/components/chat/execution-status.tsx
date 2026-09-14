import { SectionLabel } from "@/components/ui";

export function ExecutionStatus({ loading }: { loading: boolean }) {
  return <div><SectionLabel>Execution</SectionLabel><div className="rounded-xl border border-[#dbe2e7] bg-[#fbfcfc] p-4">{loading ? <div className="flex items-center gap-3 text-sm text-[#087f7b]"><span className="size-2 animate-pulse rounded-full bg-[#087f7b]" />Analyzing your question...</div> : <div className="text-sm leading-6 text-[#687684]">Tool-level execution metadata is not exposed by the current agent API. This panel is ready for future trace metadata.</div>}</div></div>;
}
