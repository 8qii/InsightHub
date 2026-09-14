"use client";

import Link from "next/link";
import { FormEvent, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getAgentRun, streamAgent } from "@/lib/api";
import type { AgentRun, Citation } from "@/lib/types";
import { Card, Logo, SectionLabel, Spinner } from "@/components/ui";
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
    <main className="min-h-screen">
      <header className="border-b border-[#dbe2e7] bg-white/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
          <Logo />
          <Link href="/dashboard" className="rounded-lg px-3 py-2 text-sm font-semibold text-[#087f7b] hover:bg-[#e4f2f0]">Open dashboard <span aria-hidden="true">→</span></Link>
        </div>
      </header>
      <div className="mx-auto grid max-w-7xl gap-8 px-5 py-10 lg:grid-cols-[1fr_360px] lg:px-8">
        <div>
          <div className="mb-10 max-w-3xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-[#bfe0dc] bg-[#eaf7f5] px-3 py-1.5 text-xs font-bold uppercase tracking-[0.16em] text-[#087f7b]"><span className="size-1.5 rounded-full bg-[#087f7b]" />Nova Retail Distribution</div>
            <h1 className="text-4xl font-semibold tracking-[-0.04em] text-[#17212b] sm:text-5xl">Ask the business<br /><span className="text-[#087f7b]">what the data knows.</span></h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-[#687684]">A traceable AI analyst for company knowledge, revenue, inventory, and policy questions.</p>
          </div>
          <Card className="overflow-hidden">
            <form onSubmit={submit} className="p-5 sm:p-7">
              <SectionLabel>Analyst question</SectionLabel>
              <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Why did Product Luna revenue decline in Q3?" rows={4} className="w-full resize-none rounded-xl border border-[#cbd6dc] bg-[#fbfcfc] p-4 text-base text-[#17212b] outline-none transition placeholder:text-[#9aa7af] focus:border-[#087f7b] focus:ring-4 focus:ring-[#087f7b]/10" aria-label="Analyst question" />
              <div className="mt-4 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                <div className="flex flex-wrap gap-2">{suggestedQuestions.map((suggestion) => <button type="button" key={suggestion} onClick={() => setQuestion(suggestion)} className="rounded-full border border-[#dbe2e7] px-3 py-1.5 text-xs text-[#687684] hover:border-[#087f7b] hover:text-[#087f7b]">{suggestion}</button>)}</div>
                <button disabled={!question.trim() || loading} className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-[#087f7b] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#075e5b] disabled:cursor-not-allowed disabled:opacity-50">{loading && <Spinner />}{loading ? "Analyzing" : "Run analysis"}</button>
              </div>
            </form>
          </Card>
          {error && <div role="alert" className="mt-5 rounded-xl border border-[#e8b8b4] bg-[#fff6f5] p-4 text-sm text-[#a33f36]">{error}</div>}
          {(loading || answer) && <Card className="mt-6 p-5 sm:p-7"><SectionLabel>Analysis</SectionLabel><div className="prose-analyst text-[15px] leading-7 text-[#31414c]"><ReactMarkdown remarkPlugins={[remarkGfm]}>{answer || "The analyst is assembling evidence..."}</ReactMarkdown></div></Card>}
        </div>
        <aside className="space-y-5">
          {answer ? <><Card className="p-5"><CitationList citations={sources} /></Card><Card className="p-5"><ExecutionStatus loading={loading} /></Card>{trace && <Card className="p-5"><TraceTimeline trace={trace} /></Card>}</> : <Card className="border-[#bfe0dc] bg-[#eaf7f5] p-6"><div className="text-3xl">✦</div><h2 className="mt-4 text-lg font-bold text-[#17212b]">Built for evidence</h2><p className="mt-2 text-sm leading-6 text-[#4d626d]">Answers combine company documents and structured business data. Citations and a sanitized trace stay attached to each run.</p><div className="mt-6 border-t border-[#bfe0dc] pt-5 text-xs font-bold uppercase tracking-[0.16em] text-[#087f7b]">Knowledge + data + context</div></Card>}
          <Card className="p-5"><SectionLabel>Available domains</SectionLabel><div className="space-y-3 text-sm">{["Company knowledge", "Sales performance", "Inventory risk", "Discount policy"].map((item) => <div className="flex items-center gap-3" key={item}><span className="size-2 rounded-full bg-[#c78028]" />{item}</div>)}</div></Card>
        </aside>
      </div>
    </main>
  );
}
