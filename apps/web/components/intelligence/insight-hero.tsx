import type { InsightPresentation } from "@/lib/intelligence-presentation";
import { ConfidenceIndicator } from "./confidence-indicator";
import { EvidenceSummary } from "./evidence-summary";
import { RecommendationBlock } from "./recommendation-block";

export function InsightHero({ insight }: { insight: InsightPresentation }) {
  return (
    <section className="grid gap-10 border-b border-line pb-12 xl:grid-cols-[minmax(0,1.25fr)_minmax(300px,.75fr)]">
      <div>
        <div className="flex flex-wrap items-center gap-3"><div className="text-label font-bold uppercase tracking-label text-brand">Executive insight</div><ConfidenceIndicator insight={insight} /></div>
        <h2 className="mt-4 max-w-4xl text-4xl font-semibold leading-[1.1] tracking-heading text-ink sm:text-5xl">{insight.headline}</h2>
        <p className="mt-5 max-w-3xl text-lg leading-8 text-ink-soft">{insight.observation}</p>
        <div className="mt-8 grid gap-6 border-t border-line pt-6 sm:grid-cols-2"><div><div className="text-label font-bold uppercase tracking-label text-muted">Why it matters</div><p className="mt-2 text-sm leading-6 text-ink-soft">This is a {insight.priority} priority observation requiring leadership attention.</p></div><EvidenceSummary insight={insight} /></div>
      </div>
      <aside className="flex flex-col justify-between border-l border-line pl-0 xl:pl-8"><div><div className="text-label font-bold uppercase tracking-label text-muted">Business impact</div><div className="mt-2 text-2xl font-semibold tracking-heading text-ink">{insight.impact}</div><div className="mt-4 text-sm text-muted">{insight.evidenceCount} evidence source{insight.evidenceCount === 1 ? "" : "s"} reviewed</div></div><div className="mt-8"><RecommendationBlock insight={insight} /></div></aside>
    </section>
  );
}
