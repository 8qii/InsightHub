"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { InvestigationStatusIndicator } from "@/components/intelligence/investigation-status-indicator";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { Spinner } from "@/components/ui/spinner";
import { getOverview } from "@/lib/api";
import {
  createEmptyWorkflowState,
  createRecentAnalysisHistory,
  createSignalQueuePresentation,
  readInvestigationWorkflow,
  syncWorkflowSignals,
  writeInvestigationWorkflow,
} from "@/lib/investigation-workflow";
import type { InvestigationWorkflowState } from "@/lib/investigation-workflow";
import type { Overview, PrioritySignal } from "@/lib/types";

type PriorityFilter = "all" | PrioritySignal["severity"];

const priorityStyles = {
  high: "border-danger text-danger",
  medium: "border-warning text-warning-strong",
  low: "border-brand text-brand",
};

function displayTimestamp(value: string) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

export function SignalsView() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [workflow, setWorkflow] = useState<InvestigationWorkflowState>(createEmptyWorkflowState);
  const [priority, setPriority] = useState<PriorityFilter>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getOverview().then((response) => {
      const next = syncWorkflowSignals(readInvestigationWorkflow(), response);
      writeInvestigationWorkflow(next);
      setWorkflow(next);
      setOverview(response);
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "The intelligence queue is unavailable.")).finally(() => setLoading(false));
  }, []);

  const queue = overview ? createSignalQueuePresentation(overview, workflow) : [];
  const visibleQueue = priority === "all" ? queue : queue.filter((item) => item.priority === priority);
  const history = createRecentAnalysisHistory(workflow);

  return (
    <AppShell page="Signals" scope={overview?.scope ?? "Intelligence queue"}>
      <main className="w-full space-y-12">
        <header className="grid gap-7 border-b border-line pb-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-end">
          <div><Badge tone="brand" compact className="mb-4 uppercase tracking-eyebrow"><span className="size-1.5 rounded-full bg-brand" />Decision workflow</Badge><h1 className="text-3xl font-semibold tracking-heading text-ink sm:text-4xl">Intelligence queue</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-muted sm:text-base">Prioritize signals, open evidence-backed investigations, and track each decision through resolution.</p></div>
          <div className="grid grid-cols-3 divide-x divide-line border-y border-line py-4 text-center"><div><div className="text-2xl font-semibold text-ink">{queue.length}</div><div className="mt-1 text-[10px] font-bold uppercase tracking-eyebrow text-muted">Signals</div></div><div><div className="text-2xl font-semibold text-ink">{queue.filter((item) => item.status === "reviewing").length}</div><div className="mt-1 text-[10px] font-bold uppercase tracking-eyebrow text-muted">Reviewing</div></div><div><div className="text-2xl font-semibold text-ink">{queue.filter((item) => item.status === "resolved").length}</div><div className="mt-1 text-[10px] font-bold uppercase tracking-eyebrow text-muted">Resolved</div></div></div>
        </header>

        {loading ? <div className="flex items-center gap-3 border-y border-line py-6 text-sm font-semibold text-ink"><Spinner /> Preparing the intelligence queue</div> : null}
        {error ? <div role="alert" className="border-l-2 border-danger bg-danger-soft px-4 py-3 text-sm text-danger">{error}</div> : null}

        {!loading && !error ? <section>
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><div className="text-label font-bold uppercase tracking-label text-brand">Active signals</div><h2 className="mt-2 text-2xl font-semibold tracking-heading text-ink">Work requiring analyst review</h2></div><div aria-label="Filter signals by priority" className="flex flex-wrap gap-2">{(["all", "high", "medium", "low"] as PriorityFilter[]).map((filter) => <button type="button" key={filter} aria-pressed={priority === filter} onClick={() => setPriority(filter)} className={`rounded-full border px-3 py-1.5 text-xs font-bold capitalize transition ${priority === filter ? "border-brand bg-brand text-white" : "border-line bg-surface text-muted hover:border-brand hover:text-brand"}`}>{filter}</button>)}</div></div>
          {visibleQueue.length ? <ol className="mt-6 divide-y divide-line border-y border-line">{visibleQueue.map((item) => <li className="grid gap-5 py-6 lg:grid-cols-[110px_minmax(0,1fr)_180px] lg:items-center" key={item.id}><div><span className={`inline-flex border-l-2 pl-2 text-[10px] font-bold uppercase tracking-eyebrow ${priorityStyles[item.priority]}`}>{item.priority} priority</span></div><div><div className="flex flex-wrap items-center gap-3"><h3 className="text-lg font-semibold tracking-heading text-ink">{item.title}</h3><InvestigationStatusIndicator status={item.status} /></div><p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{item.summary}</p><div className="mt-3 text-xs font-semibold text-ink-soft">{item.metric}</div></div><div className="lg:text-right"><div className="text-[10px] font-bold uppercase tracking-eyebrow text-muted">Updated {displayTimestamp(item.updatedAt)}</div><Link href={item.href} className="mt-3 inline-flex items-center gap-2 text-sm font-bold text-brand hover:text-brand-strong focus-visible:outline-none focus-visible:shadow-focus">Open investigation <span aria-hidden="true">-&gt;</span></Link></div></li>)}</ol> : <EmptyState title="No signals match this priority." description="Choose another priority to return to the active intelligence queue." className="mt-6 bg-surface-subtle" />}
        </section> : null}

        {!loading && !error ? <section className="grid gap-7 border-t border-line pt-10 lg:grid-cols-[260px_minmax(0,1fr)]"><div><div className="text-label font-bold uppercase tracking-label text-brand">Recent analysis</div><h2 className="mt-2 text-2xl font-semibold tracking-heading text-ink">Workspace history</h2><p className="mt-2 text-sm leading-6 text-muted">Local activity from investigation opens, completed analysis, and lifecycle decisions.</p></div>{history.length ? <ol className="divide-y divide-line border-y border-line">{history.map((item) => <li className="flex flex-col justify-between gap-3 py-4 sm:flex-row sm:items-center" key={item.id}><div><div className="text-sm font-semibold text-ink">{item.title}</div><div className="mt-1 text-xs text-muted">{item.action}</div></div><div className="flex items-center gap-4"><time className="text-[10px] font-bold uppercase tracking-eyebrow text-muted" dateTime={item.occurredAt}>{displayTimestamp(item.occurredAt)}</time><Link href={item.href} className="text-xs font-bold text-brand hover:text-brand-strong">Review</Link></div></li>)}</ol> : <EmptyState title="No analysis activity yet." description="Open an investigation to begin building local workspace history." />}</section> : null}
      </main>
    </AppShell>
  );
}
