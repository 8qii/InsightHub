import { InvestigationView } from "@/components/intelligence/investigation-view";

export default async function InvestigationPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <InvestigationView investigationId={id} />;
}
