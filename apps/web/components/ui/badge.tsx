import type { HTMLAttributes } from "react";

type BadgeTone = "brand" | "neutral" | "warning";

const toneClasses: Record<BadgeTone, string> = {
  brand: "border-brand-border bg-brand-soft text-brand",
  neutral: "border-line bg-surface-subtle text-muted",
  warning: "border-warning-border bg-warning-soft text-warning-strong",
};

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  compact?: boolean;
  tone?: BadgeTone;
}

export function Badge({ className = "", compact = false, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 text-xs font-bold ${compact ? "py-1" : "py-1.5"} ${toneClasses[tone]} ${className}`}
      {...props}
    />
  );
}
