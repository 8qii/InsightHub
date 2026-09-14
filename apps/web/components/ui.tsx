export function Logo() {
  return (
    <div className="flex items-center gap-3">
      <div className="grid size-9 place-items-center rounded-xl bg-[#087f7b] text-lg font-bold text-white shadow-sm">I</div>
      <div><div className="text-sm font-bold tracking-[0.18em] text-[#17212b]">INSIGHTHUB</div><div className="text-[10px] uppercase tracking-[0.2em] text-[#687684]">Enterprise analyst</div></div>
    </div>
  );
}

export function SectionLabel({ children }: { children: React.ReactNode }) {
  return <div className="mb-3 text-[11px] font-bold uppercase tracking-[0.2em] text-[#687684]">{children}</div>;
}

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-[#dbe2e7] bg-white shadow-[0_12px_35px_rgba(23,33,43,0.04)] ${className}`}>{children}</section>;
}

export function Spinner() {
  return <span className="inline-block size-4 animate-spin rounded-full border-2 border-current border-t-transparent" aria-label="Loading" />;
}
