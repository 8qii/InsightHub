import type { ReactNode } from "react";

export function WorkspaceContainer({ children }: { children: ReactNode }) {
  return <div className="w-full flex-1 px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10 xl:px-10">{children}</div>;
}
