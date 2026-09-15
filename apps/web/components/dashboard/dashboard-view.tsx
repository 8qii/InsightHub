"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { InsightHero } from "@/components/intelligence/insight-hero";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { Spinner } from "@/components/ui/spinner";
import { getOverview } from "@/lib/api";
import { createOverviewPresentation } from "@/lib/intelligence-presentation";
import type { Overview } from "@/lib/types";

function displayDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

const severityStyles = {
  high: "border-danger text-danger",
  medium: "border-warning text-warning-strong",
  low: "border-brand text-brand",
};

const evidenceTypeStyles = {
  document: "bg-warning",
  database: "bg-brand",
  metric: "bg-ink-soft",
};

export function DashboardView() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const briefing = overview ? createOverviewPresentation(overview) : null;

  useEffect(() => {
    getOverview()
      .then(setOverview)
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Executive overview is unavailable."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell page="Overview" scope={briefing?.scope ?? "Loading"}>
      <main className="w-full space-y-14">
        <header className="flex flex-col justify-between gap-6 border-b border-line pb-7 lg:flex-row lg:items-end">
          <div>
            <Badge tone="brand" compact className="mb-4 uppercase tracking-eyebrow"><span className="size-1.5 rounded-full bg-brand" />Executive intelligence briefing</Badge>
            <h1 className="text-3xl font-semibold tracking-heading text-ink sm:text-4xl">{briefing ? `${briefing.company} executive briefing` : "Executive intelligence briefing"}</h1>
          </div>
          <div className="border-l-2 border-brand pl-4 text-sm"><div className="text-label font-bold uppercase tracking-label text-brand">{briefing?.preparationStatus ?? "Analyst preparing"}</div><div className="mt-1 font-semibold text-ink">{briefing ? displayDate(briefing.asOfDate) : "Reviewing sources"}</div><div className="mt-1 text-xs text-muted">{briefing ? `${briefing.period} · ${briefing.evidenceCount} evidence source${briefing.evidenceCount === 1 ? "" : "s"}` : "Building the executive report"}</div></div>
        </header>

        {loading ? <section aria-live="polite" className="border-y border-line py-8"><div className="flex items-center gap-3 text-sm font-semibold text-ink"><Spinner /> Analyst is preparing your briefing</div><div className="mt-5 grid gap-3 text-sm text-muted sm:grid-cols-3"><div className="border-l-2 border-brand pl-3">Reviewing reporting context</div><div className="border-l-2 border-line-strong pl-3">Linking source evidence</div><div className="border-l-2 border-line-strong pl-3">Preparing recommendations</div></div></section> : null}
        {error ? <div role="alert" className="border-l-2 border-danger bg-danger-soft px-4 py-3 text-sm text-danger">{error}</div> : null}

        {briefing ? <>
          {briefing.insight ? <InsightHero insight={briefing.insight} /> : <EmptyState title="No executive finding requires attention." description="The analyst reviewed the available signals and did not identify a prioritized observation for this reporting period." className="border-solid bg-surface-subtle p-6" />}

          <section className="grid gap-8 border-b border-line pb-12 lg:grid-cols-[260px_minmax(0,1fr)]">
            <div><div className="text-label font-bold uppercase tracking-label text-brand">Evidence relationship</div><h2 className="mt-3 text-2xl font-semibold tracking-heading text-ink">Finding to evidence</h2><p className="mt-2 text-sm leading-6 text-muted">The conclusion is grounded in explicitly classified source relationships.</p></div>
            <div className="border-l border-line pl-5">
              <div className="text-sm font-semibold text-ink">Finding: {briefing.evidenceRelationship.finding}</div>
              {briefing.evidenceRelationship.supportingEvidence.length ? <ol className="mt-5 space-y-4">
                {briefing.evidenceRelationship.supportingEvidence.map((evidence) => <li className="grid gap-3 sm:grid-cols-[130px_minmax(0,1fr)]" key={evidence.id}><div className="flex items-start gap-3 text-[10px] font-bold uppercase tracking-eyebrow text-muted"><span className={`mt-1 size-2 rounded-full ${evidenceTypeStyles[evidence.sourceType]}`} />{evidence.sourceLabel}</div><div><div className="flex flex-wrap items-baseline gap-x-3 gap-y-1"><div className="text-sm font-semibold text-ink">{evidence.title}</div><div className="text-[10px] font-bold uppercase tracking-eyebrow text-muted">{evidence.roleLabel}</div></div><p className="mt-1 text-sm leading-6 text-muted">{evidence.detail}</p></div></li>)}
              </ol> : <EmptyState title="No evidence sources are available." description="The next briefing will show linked document, database, or metric evidence when it is available." className="mt-5" />}
            </div>
          </section>

          <section className="grid gap-8 border-b border-line pb-12 lg:grid-cols-[260px_minmax(0,1fr)]">
            <div><div className="text-label font-bold uppercase tracking-label text-brand">Supporting context</div><h2 className="mt-3 text-2xl font-semibold tracking-heading text-ink">Business measures</h2><p className="mt-2 text-sm leading-6 text-muted">Context for the briefing, not a dashboard to interpret.</p></div>
            <dl className="grid gap-x-8 gap-y-6 sm:grid-cols-2 xl:grid-cols-4">{briefing.metrics.map((metric) => <div className="border-l border-line pl-4" key={metric.label}><dt className="text-label font-bold uppercase tracking-label text-muted">{metric.label}</dt><dd className="mt-2 text-xl font-semibold tracking-heading text-ink">{metric.value}</dd><div className="mt-1 text-xs leading-5 text-muted">{metric.detail}</div></div>)}</dl>
          </section>

          <section className="grid gap-8 lg:grid-cols-[260px_minmax(0,1fr)]">
            <div><div className="text-label font-bold uppercase tracking-label text-brand">Attention queue</div><h2 className="mt-3 text-2xl font-semibold tracking-heading text-ink">Decisions waiting for follow-up</h2><p className="mt-2 text-sm leading-6 text-muted">Each situation includes its current impact and a direct route to investigate.</p></div>
            {briefing.attention.length ? <ol className="divide-y divide-line border-y border-line">{briefing.attention.map((item) => <li className="grid gap-5 py-6 md:grid-cols-[110px_minmax(0,1fr)_180px] md:items-start" key={item.id}><div><span className={`inline-flex border-l-2 pl-2 text-[10px] font-bold uppercase tracking-eyebrow ${severityStyles[item.severity]}`}>{item.severity}</span></div><div><h3 className="text-lg font-semibold tracking-heading text-ink">{item.title}</h3><p className="mt-2 text-sm leading-6 text-muted">{item.observation}</p><div className="mt-3 text-xs font-semibold text-muted">{item.evidenceCount} linked evidence source{item.evidenceCount === 1 ? "" : "s"}</div></div><div className="md:text-right"><div className="text-sm font-bold text-ink">{item.impact}</div><Link href={item.actionHref} className="mt-4 inline-flex items-center gap-2 text-sm font-bold text-brand hover:text-brand-strong focus-visible:outline-none focus-visible:shadow-focus">{item.action} <span aria-hidden="true">-&gt;</span></Link></div></li>)}</ol> : <EmptyState title="No follow-up decisions are waiting." description="The analyst did not find a signal requiring an immediate investigation." className="border-solid bg-surface-subtle" />}
          </section>
        </> : null}
      </main>
    </AppShell>
  );
}
