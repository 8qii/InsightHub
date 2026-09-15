import type { HTMLAttributes } from "react";

type CardTone = "default" | "brand" | "editorial" | "utility";

interface CardProps extends HTMLAttributes<HTMLElement> {
  tone?: CardTone;
}

const toneClasses: Record<CardTone, string> = {
  default: "border-line bg-surface shadow-card",
  brand: "border-brand-border bg-brand-soft shadow-card",
  editorial: "border-line-strong bg-surface shadow-editorial",
  utility: "border-line bg-surface-subtle shadow-none",
};

export function Card({ className = "", tone = "default", ...props }: CardProps) {
  return <section className={`rounded-card border ${toneClasses[tone]} ${className}`} {...props} />;
}
