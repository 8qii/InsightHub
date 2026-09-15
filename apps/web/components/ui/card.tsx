import type { HTMLAttributes } from "react";

type CardTone = "default" | "brand";

interface CardProps extends HTMLAttributes<HTMLElement> {
  tone?: CardTone;
}

const toneClasses: Record<CardTone, string> = {
  default: "border-line bg-surface",
  brand: "border-brand-border bg-brand-soft",
};

export function Card({ className = "", tone = "default", ...props }: CardProps) {
  return <section className={`rounded-card border shadow-card ${toneClasses[tone]} ${className}`} {...props} />;
}
