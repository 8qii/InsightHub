export function Logo({ inverse = false }: { inverse?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className={`grid size-9 place-items-center rounded-control text-lg font-bold text-white shadow-sm ${inverse ? "bg-brand-muted" : "bg-brand"}`}>I</div>
      <div>
        <div className={`text-sm font-bold tracking-brand ${inverse ? "text-white" : "text-ink"}`}>INSIGHTHUB</div>
        <div className={`text-brand-caption uppercase tracking-label ${inverse ? "text-white/55" : "text-muted"}`}>Enterprise analyst</div>
      </div>
    </div>
  );
}
