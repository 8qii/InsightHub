import Link from "next/link";
import type { InsightPresentation } from "@/lib/intelligence-presentation";

export function RecommendationBlock({ insight }: { insight: InsightPresentation }) {
  return (
    <div className="border-l-2 border-brand pl-4">
      <div className="text-label font-bold uppercase tracking-label text-brand">Recommended action</div>
      <Link href={insight.recommendationHref} className="mt-2 inline-flex items-center gap-2 text-sm font-bold text-brand hover:text-brand-strong focus-visible:outline-none focus-visible:shadow-focus">{insight.recommendation} <span aria-hidden="true">-&gt;</span></Link>
    </div>
  );
}
