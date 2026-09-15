import Link from "next/link";
import { Logo } from "./logo";

interface AppHeaderProps {
  actionHref: string;
  actionLabel: string;
}

export function AppHeader({ actionHref, actionLabel }: AppHeaderProps) {
  return (
    <header className="border-b border-line bg-surface/90">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
        <Logo />
        <Link href={actionHref} className="rounded-action px-3 py-2 text-sm font-semibold text-brand transition hover:bg-brand-subtle">
          {actionLabel} <span aria-hidden="true">→</span>
        </Link>
      </div>
    </header>
  );
}
