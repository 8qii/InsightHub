"use client";

import { FormEvent, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getAgentRun, streamAgent } from "@/lib/api";
import type { AgentRun, Citation } from "@/lib/types";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { SectionLabel } from "@/components/ui/section-header";
import { Spinner } from "@/components/ui/spinner";
import { CitationList } from "./citation-list";
import { ExecutionStatus } from "./execution-status";
import { TraceTimeline } from "./trace-timeline";

const suggestedQuestions = [
  "Why did Product Luna revenue decline in Q3?",
  "What is the maximum VIP discount allowed?",
  "Which products have aging inventory?",
];

export function AnalystChat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Citation[]>([]);
  const [trace, setTrace] = useState<AgentRun | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || loading) return;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError(null);
    setAnswer("");
    setSources([]);
    setTrace(null);
    try {
      await streamAgent(trimmed, {
        onToken: (text) => setAnswer((current) => current + text),
        onDone: (nextSources, runId) => {
          setSources(nextSources);
          void getAgentRun(runId).then(setTrace).catch(() => undefined);
        },
      }, controller.signal);
    } catch (reason) {
      if (!(reason instanceof DOMException && reason.name === "AbortError")) {
        setError(reason instanceof Error ? reason.message : "The analyst could not complete this request.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell page="Analyst" scope="All products">
      <main className="grid w-full gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="min-w-0">
          <div className="mb-6 border-b border-line pb-6">
            <Badge tone="brand" compact className="mb-3 uppercase tracking-eyebrow"><span className="size-1.5 rounded-full bg-brand" />Cross-source intelligence</Badge>
            <h1 className="text-3xl font-semibold tracking-heading text-ink">Intelligence analyst</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">Ask questions across company knowledge, revenue, inventory, and policy data with traceable evidence.</p>
          </div>
          <Card className="overflow-hidden">
            <form onSubmit={submit} className="p-5 sm:p-7">
              <SectionLabel>Analyst question</SectionLabel>
              <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Why did Product Luna revenue decline in Q3?" rows={4} className="w-full resize-none rounded-control border border-line-strong bg-surface-subtle p-4 text-base text-ink outline-none transition placeholder:text-placeholder focus:border-brand focus:shadow-focus" aria-label="Analyst question" />
              <div className="mt-4 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                <div className="flex flex-wrap gap-2">{suggestedQuestions.map((suggestion) => <Button variant="secondary" size="sm" key={suggestion} onClick={() => setQuestion(suggestion)}>{suggestion}</Button>)}</div>
                <Button type="submit" disabled={!question.trim() || loading} className="shrink-0">{loading && <Spinner />}{loading ? "Analyzing" : "Run analysis"}</Button>
              </div>
            </form>
          </Card>
          {error && <div role="alert" className="mt-5 rounded-control border border-danger-border bg-danger-soft p-4 text-sm text-danger">{error}</div>}
          {(loading || answer) && <Card className="mt-6 p-5 sm:p-7"><SectionLabel>Analysis</SectionLabel><div className="prose-analyst text-[15px] leading-7 text-ink-soft"><ReactMarkdown remarkPlugins={[remarkGfm]}>{answer || "The analyst is assembling evidence..."}</ReactMarkdown></div></Card>}
        </div>
        <aside className="space-y-5 xl:border-l xl:border-line xl:pl-6">
          {answer ? <><Card className="p-5"><CitationList citations={sources} /></Card><Card className="p-5"><ExecutionStatus loading={loading} /></Card>{trace && <Card className="p-5"><TraceTimeline trace={trace} /></Card>}</> : <Card tone="brand" className="p-6"><div className="text-3xl">✦</div><h2 className="mt-4 text-lg font-bold text-ink">Built for evidence</h2><p className="mt-2 text-sm leading-6 text-ink-soft">Answers combine company documents and structured business data. Citations and a sanitized trace stay attached to each run.</p><div className="mt-6 border-t border-brand-border pt-5 text-xs font-bold uppercase tracking-eyebrow text-brand">Knowledge + data + context</div></Card>}
          <Card className="p-5"><SectionLabel>Available domains</SectionLabel><div className="space-y-3 text-sm">{["Company knowledge", "Sales performance", "Inventory risk", "Discount policy"].map((item) => <div className="flex items-center gap-3" key={item}><span className="size-2 rounded-full bg-warning" />{item}</div>)}</div></Card>
        </aside>
      </main>
    </AppShell>
  );
}
