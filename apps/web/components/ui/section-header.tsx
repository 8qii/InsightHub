import type { ReactNode } from "react";

interface SectionLabelProps {
  children: ReactNode;
  className?: string;
  tone?: "brand" | "muted";
}

export function SectionLabel({ children, className = "", tone = "muted" }: SectionLabelProps) {
  return <div className={`mb-3 text-label font-bold uppercase tracking-label ${tone === "brand" ? "text-brand" : "text-muted"} ${className}`}>{children}</div>;
}

interface SectionHeaderProps {
  title: string;
  description?: string;
  eyebrow?: string;
  action?: ReactNode;
  className?: string;
}

export function SectionHeader({ action, className = "", description, eyebrow, title }: SectionHeaderProps) {
  return (
    <div className={`flex flex-col justify-between gap-4 sm:flex-row sm:items-end ${className}`}>
      <div>
        {eyebrow ? <SectionLabel tone="brand">{eyebrow}</SectionLabel> : null}
        <h2 className="text-2xl font-semibold tracking-heading text-ink">{title}</h2>
        {description ? <p className="mt-2 leading-6 text-muted">{description}</p> : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
