"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getInvestigation } from "@/lib/api";
import type { Investigation } from "@/lib/types";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/section-header";
import { Spinner } from "@/components/ui/spinner";
import {
  createActivityTimeline,
  createEmptyWorkflowState,
  ensureInvestigationRecord,
  investigationStatusLabels,
  investigationStatuses,
  readInvestigationWorkflow,
  recordAnalysisCompleted,
  recordInvestigationOpen,
  updateInvestigationStatus,
  writeInvestigationWorkflow,
} from "@/lib/investigation-workflow";
import type { InvestigationStatus, InvestigationWorkflowState } from "@/lib/investigation-workflow";
import { DriverBreakdown } from "./driver-breakdown";
import { EvidenceTimeline } from "./evidence-timeline";
import { FindingCard } from "./finding-card";
import { InvestigationActivityTimeline } from "./investigation-activity-timeline";
import { InvestigationStatusIndicator } from "./investigation-status-indicator";
import { QuestionSuggestion } from "./question-suggestion";

function displayDate(value: string) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" }).format(new Date(`${value}T00:00:00Z`));
}

export function InvestigationView({ investigationId }: { investigationId: string }) {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [workflow, setWorkflow] = useState<InvestigationWorkflowState>(createEmptyWorkflowState);
  const workflowRecord = workflow.records[investigationId];

  function persistWorkflow(next: InvestigationWorkflowState) {
    writeInvestigationWorkflow(next);
    setWorkflow(next);
  }

  useEffect(() => {
    const stored = readInvestigationWorkflow();
    const opened = stored.records[investigationId] ? recordInvestigationOpen(stored, investigationId, new Date().toISOString()) : stored;
    writeInvestigationWorkflow(opened);
    queueMicrotask(() => setWorkflow(opened));
    getInvestigation(investigationId).then((response) => {
      setInvestigation(response);
      let next = readInvestigationWorkflow();
      next = ensureInvestigationRecord(next, investigationId, {
        title: response.title,
        summary: response.executive_summary,
        metric: response.impact,
        priority: response.findings[0]?.severity ?? "medium",
      }, `${response.as_of_date}T00:00:00.000Z`);
      if (!next.records[investigationId]?.lastOpenedAt) next = recordInvestigationOpen(next, investigationId, new Date().toISOString());
      next = recordAnalysisCompleted(next, investigationId, new Date().toISOString());
      persistWorkflow(next);
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Investigation is unavailable.")).finally(() => setLoading(false));
  }, [investigationId]);

  function handleStatusChange(status: InvestigationStatus) {
    persistWorkflow(updateInvestigationStatus(workflow, investigationId, status, new Date().toISOString()));
  }

  return (
    <AppShell page="Investigation" scope={investigation?.title ?? workflowRecord?.snapshot.title ?? "Signal review"}>
      <main className="w-full space-y-12">
        <section className="rounded-card border border-brand-border bg-[linear-gradient(120deg,var(--color-surface)_0%,var(--color-brand-soft)_100%)] px-5 py-7 shadow-editorial sm:px-8 sm:py-9">
          <Link href="/dashboard/signals" className="inline-flex items-center gap-2 text-sm font-bold text-brand hover:text-brand-strong focus-visible:outline-none focus-visible:shadow-focus">&lt;- Back to intelligence queue</Link>
          <div className="mt-6 flex flex-col justify-between gap-7 lg:flex-row lg:items-end">
            <div><Badge tone="brand" compact className="mb-4 uppercase tracking-eyebrow"><span className="size-1.5 rounded-full bg-brand" />Investigation workspace</Badge><h1 className="max-w-3xl text-3xl font-semibold tracking-heading text-ink sm:text-4xl">{investigation?.title ?? workflowRecord?.snapshot.title ?? "Signal investigation"}</h1><p className="mt-3 max-w-3xl text-sm leading-6 text-ink-soft sm:text-base">A curated evidence workspace for validating the signal, assessing its impact, and selecting the next analytical question.</p></div>
            <div className="min-w-64 rounded-control border border-brand-border bg-surface/85 p-4 shadow-card"><div className="flex items-center justify-between gap-3"><div className="text-label font-bold uppercase tracking-label text-brand">Lifecycle</div>{workflowRecord ? <InvestigationStatusIndicator status={workflowRecord.status} /> : null}</div><label className="mt-4 block text-xs font-semibold text-muted" htmlFor="investigation-status">Update status</label><select id="investigation-status" value={workflowRecord?.status ?? "new"} disabled={!workflowRecord} onChange={(event) => handleStatusChange(event.target.value as InvestigationStatus)} className="mt-2 w-full rounded-action border border-line bg-surface px-3 py-2 text-sm font-semibold text-ink focus:border-brand focus:outline-none focus:shadow-focus">{investigationStatuses.map((status) => <option value={status} key={status}>{investigationStatusLabels[status]}</option>)}</select><div className="mt-3 text-xs text-muted">Evidence current {investigation ? displayDate(investigation.as_of_date) : "when analysis is available"}</div></div>
          </div>
        </section>
        {loading ? <div className="flex items-center gap-3 rounded-control border border-brand-border bg-brand-soft p-4 text-sm text-brand"><Spinner /> Preparing investigation evidence...</div> : null}
        {error ? <div role="alert" className="rounded-control border border-danger-border bg-danger-soft p-4 text-sm text-danger">{error}</div> : null}
        {workflowRecord ? <section className="grid gap-7 border-y border-line py-9 lg:grid-cols-[260px_minmax(0,1fr)]"><div><div className="text-label font-bold uppercase tracking-label text-brand">Investigation activity</div><h2 className="mt-2 text-2xl font-semibold tracking-heading text-ink">Decision timeline</h2><p className="mt-2 text-sm leading-6 text-muted">Milestones show how the signal moved from detection to a tracked decision.</p></div><InvestigationActivityTimeline items={createActivityTimeline(workflowRecord, workflow.interactions)} /></section> : null}
        {investigation ? <>
          <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]"><Card tone="editorial" className="border-t-4 border-t-brand p-6 sm:p-8"><div className="text-label font-bold uppercase tracking-label text-brand">Conclusion</div><p className="mt-4 text-xl font-semibold leading-8 tracking-heading text-ink sm:text-2xl">{investigation.conclusion}</p><p className="mt-5 border-t border-line pt-5 text-sm leading-6 text-ink-soft">{investigation.executive_summary}</p></Card><Card tone="brand" className="flex flex-col justify-between p-6"><div><div className="text-label font-bold uppercase tracking-label text-brand">Business impact</div><div className="mt-5 text-2xl font-semibold leading-8 tracking-heading text-ink">{investigation.impact}</div></div><div className="mt-6 border-t border-brand-border pt-4 text-xs font-bold uppercase tracking-eyebrow text-brand">{investigation.period} comparison</div></Card></section>
          <section><SectionHeader eyebrow="Key findings" title="What the signal indicates" description="Curated observations distinguish measured performance from supporting business context." className="mb-5" /><div className="grid gap-4 lg:grid-cols-3">{investigation.findings.map((finding) => <FindingCard finding={finding} key={finding.title} />)}</div></section>
          <section className="border-y border-line py-10"><SectionHeader eyebrow="Driver breakdown" title="What to validate before acting" description="Each driver frames a distinct line of investigation rather than assigning a single cause." className="mb-5" /><DriverBreakdown drivers={investigation.drivers} /></section>
          <section className="grid gap-8 xl:grid-cols-[minmax(0,.75fr)_minmax(0,1.25fr)]"><SectionHeader eyebrow="Evidence timeline" title="The evidence behind the conclusion" description="Metric inputs and supporting documents are explicitly distinguished and arranged by reporting date." /><div className="border-l border-line pl-3 sm:pl-5"><EvidenceTimeline evidence={investigation.evidence} /></div></section>
          <section className="rounded-card border border-line bg-surface-subtle px-4 py-7 sm:px-7 sm:py-8"><SectionHeader eyebrow="Next questions" title="Continue the investigation" description="Open Analyst to investigate a targeted follow-up with the existing agent workflow." className="mb-6" /><div className="grid gap-5 lg:grid-cols-3">{investigation.suggested_questions.map((suggestion, index) => <QuestionSuggestion index={index + 1} suggestion={suggestion} key={suggestion.question} />)}</div></section>
        </> : null}
      </main>
    </AppShell>
  );
}
