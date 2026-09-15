"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { Logo } from "./logo";

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

type NavIcon = "analyst" | "evidence" | "overview" | "signals";

const navigation: Array<{ label: string; href?: string; icon: NavIcon }> = [
  { label: "Overview", href: "/dashboard", icon: "overview" },
  { label: "Analyst", href: "/", icon: "analyst" },
  { label: "Signals", href: "/dashboard/signals", icon: "signals" },
  { label: "Evidence", icon: "evidence" },
];

function NavigationIcon({ name }: { name: NavIcon }) {
  const paths: Record<NavIcon, React.ReactNode> = {
    overview: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
    analyst: <><path d="M4 19V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8l-4 2Z" /><path d="M8 8h8M8 12h5" /></>,
    signals: <><path d="M4 18V9M10 18V5M16 18v-7M22 18V3" /><path d="M2 18h22" /></>,
    evidence: <><path d="M6 3h9l4 4v14H6z" /><path d="M14 3v5h5M9 13h7M9 17h5" /></>,
  };

  return <svg viewBox="0 0 24 24" aria-hidden="true" className="size-5 fill-none stroke-current stroke-[1.7]">{paths[name]}</svg>;
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <>
      <div className="flex h-20 items-center border-b border-white/10 px-6">
        <Logo inverse />
      </div>
      <div className="flex-1 px-3 py-6">
        <div className="px-3 text-label font-bold uppercase tracking-label text-white/40">Workspace</div>
        <nav className="mt-3 space-y-1">
          {navigation.map((item) => {
            const active = item.href === "/dashboard"
              ? pathname === "/dashboard"
              : item.href === pathname;
            if (!item.href) {
              return (
                <div className="flex items-center gap-3 rounded-control px-3 py-2.5 text-sm text-white/40" key={item.label} aria-disabled="true">
                  <NavigationIcon name={item.icon} />
                  <span>{item.label}</span>
                  <span className="ml-auto rounded-full border border-white/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-eyebrow">Soon</span>
                </div>
              );
            }
            return (
              <Link
                href={item.href}
                key={item.label}
                onClick={onNavigate}
                aria-current={active ? "page" : undefined}
                className={`relative flex items-center gap-3 rounded-control px-3 py-2.5 text-sm font-semibold transition ${active ? "bg-white/10 text-white ring-1 ring-inset ring-white/5 before:absolute before:-left-3 before:h-6 before:w-0.5 before:rounded-full before:bg-brand-muted" : "text-white/65 hover:bg-white/5 hover:text-white"}`}
              >
                <NavigationIcon name={item.icon} />
                {item.label}
                {active ? <span className="ml-auto size-1.5 rounded-full bg-brand-muted" /> : null}
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="border-t border-white/10 p-5">
        <div className="rounded-control border border-white/10 bg-white/[0.06] p-3.5 ring-1 ring-inset ring-white/5">
          <div className="flex items-center gap-2 text-xs font-semibold text-white/85"><span className="size-2 rounded-full bg-brand-muted ring-4 ring-brand-muted/10" />Systems connected</div>
          <div className="mt-2 text-xs leading-5 text-white/45">Knowledge and operational data are current for this workspace.</div>
        </div>
      </div>
    </>
  );
}

export function Sidebar({ onClose, open }: SidebarProps) {
  const drawerRef = useRef<HTMLElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    closeButtonRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
        return;
      }
      if (event.key !== "Tab" || !drawerRef.current) return;
      const focusable = Array.from(drawerRef.current.querySelectorAll<HTMLElement>('button:not([disabled]), a[href]'));
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose, open]);

  return (
    <>
      <aside aria-label="Primary navigation" className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col bg-ink text-white lg:flex">
        <SidebarContent />
      </aside>
      {open ? (
        <>
          <button type="button" aria-label="Close navigation" className="fixed inset-0 z-40 bg-ink/35 backdrop-blur-[1px] lg:hidden" onClick={onClose} />
          <aside id="mobile-navigation" ref={drawerRef} role="dialog" aria-modal="true" aria-label="Primary navigation" className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-ink text-white shadow-2xl lg:hidden">
            <button ref={closeButtonRef} type="button" onClick={onClose} aria-label="Close navigation" className="absolute right-3 top-3 grid size-9 place-items-center rounded-action text-white/65 hover:bg-white/10 hover:text-white">
              <svg viewBox="0 0 24 24" aria-hidden="true" className="size-5 fill-none stroke-current stroke-2"><path d="m6 6 12 12M18 6 6 18" /></svg>
            </button>
            <SidebarContent onNavigate={onClose} />
          </aside>
        </>
      ) : null}
    </>
  );
}
