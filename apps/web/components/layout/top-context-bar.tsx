import type { RefObject } from "react";

interface TopContextBarProps {
  menuButtonRef: RefObject<HTMLButtonElement | null>;
  navigationOpen: boolean;
  onMenuToggle: () => void;
  page: string;
  scope: string;
}

const contextDefaults = {
  company: "Nova Retail",
  period: "Q3 2025",
  freshness: "Sep 30 2025",
};

export function TopContextBar({ menuButtonRef, navigationOpen, onMenuToggle, page, scope }: TopContextBarProps) {
  const context = [
    { label: "Company", value: contextDefaults.company },
    { label: "Period", value: contextDefaults.period },
    { label: "Scope", value: scope },
    { label: "Data freshness", value: contextDefaults.freshness },
  ];

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-surface/95 backdrop-blur">
      <div className="flex min-h-16 flex-col lg:flex-row lg:items-stretch">
        <div className="flex items-center gap-3 border-b border-line px-4 py-3 sm:px-6 lg:w-48 lg:border-b-0 lg:border-r lg:px-5">
          <button ref={menuButtonRef} type="button" onClick={onMenuToggle} aria-label={navigationOpen ? "Close navigation" : "Open navigation"} aria-expanded={navigationOpen} aria-controls="mobile-navigation" className="grid size-9 place-items-center rounded-action border border-line text-ink-soft hover:bg-surface-muted lg:hidden">
            <svg viewBox="0 0 24 24" aria-hidden="true" className="size-5 fill-none stroke-current stroke-2"><path d="M4 7h16M4 12h16M4 17h16" /></svg>
          </button>
          <div>
            <div className="text-label font-bold uppercase tracking-label text-muted">Workspace</div>
            <div className="mt-0.5 text-sm font-semibold text-ink">{page}</div>
          </div>
        </div>
        <div className="grid flex-1 grid-cols-2 sm:grid-cols-4">
          {context.map((item) => (
            <div className="min-w-0 border-r border-line px-4 py-3 last:border-r-0 sm:px-5" key={item.label}>
              <div className="text-[10px] font-bold uppercase tracking-eyebrow text-muted">{item.label}</div>
              <div className="mt-1 text-xs font-semibold leading-5 text-ink-soft sm:text-sm">{item.value}</div>
            </div>
          ))}
        </div>
      </div>
    </header>
  );
}
