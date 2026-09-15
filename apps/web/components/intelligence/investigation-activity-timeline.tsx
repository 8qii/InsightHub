import type { ActivityTimelineItemPresentation } from "@/lib/investigation-workflow";

function displayTimestamp(value: string) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

const markerStyles = {
  complete: "border-brand bg-brand",
  current: "border-warning bg-warning-soft",
  upcoming: "border-line-strong bg-surface",
};

export function InvestigationActivityTimeline({ items }: { items: ActivityTimelineItemPresentation[] }) {
  return (
    <ol className="space-y-0">
      {items.map((item, index) => (
        <li className="relative grid grid-cols-[24px_minmax(0,1fr)] gap-3 pb-6 last:pb-0" key={item.id}>
          {index < items.length - 1 ? <span className="absolute bottom-0 left-[11px] top-5 w-px bg-line" /> : null}
          <span className={`relative mt-1 size-3 rounded-full border-2 ${markerStyles[item.state]}`} />
          <div>
            <div className="flex flex-wrap items-baseline justify-between gap-2"><div className="text-sm font-semibold text-ink">{item.title}</div>{item.occurredAt ? <time className="text-[10px] font-bold uppercase tracking-eyebrow text-muted" dateTime={item.occurredAt}>{displayTimestamp(item.occurredAt)}</time> : null}</div>
            <p className="mt-1 text-xs leading-5 text-muted">{item.detail}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
