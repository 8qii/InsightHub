import type { ReactNode } from "react";

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  className?: string;
}

export function EmptyState({ className = "", description, icon, title }: EmptyStateProps) {
  return (
    <div className={`rounded-control border border-dashed border-line p-4 text-sm text-muted ${className}`}>
      {icon ? <div className="mb-2 text-brand">{icon}</div> : null}
      <div className="font-medium text-ink-soft">{title}</div>
      {description ? <p className="mt-1 leading-6">{description}</p> : null}
    </div>
  );
}
