import { SectionLabel } from "@/components/ui/section-header";

export function ExecutionStatus({ loading }: { loading: boolean }) {
  return <div><SectionLabel>Execution</SectionLabel><div className="rounded-control border border-line bg-surface-subtle p-4">{loading ? <div className="flex items-center gap-3 text-sm text-brand"><span className="size-2 animate-pulse rounded-full bg-brand" />Analyzing your question...</div> : <div className="text-sm leading-6 text-muted">Answer complete. The trace below contains metadata only: tool names, durations, and status.</div>}</div></div>;
}
