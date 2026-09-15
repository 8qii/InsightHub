import type { InsightPresentation } from "@/lib/intelligence-presentation";

export function EvidenceSummary({ insight }: { insight: InsightPresentation }) {
  return (
    <div>
      <div className="text-label font-bold uppercase tracking-label text-muted">Evidence supporting it</div>
      <p className="mt-2 text-sm leading-6 text-ink-soft">{insight.evidenceSummary}</p>
    </div>
  );
}
