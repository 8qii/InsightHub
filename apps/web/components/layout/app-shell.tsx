"use client";

import type { ReactNode } from "react";
import { useRef, useState } from "react";
import { Sidebar } from "./sidebar";
import { TopContextBar } from "./top-context-bar";
import { WorkspaceContainer } from "./workspace-container";

interface AppShellProps {
  children: ReactNode;
  page: string;
  scope: string;
}

export function AppShell({ children, page, scope }: AppShellProps) {
  const [navigationOpen, setNavigationOpen] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  function closeNavigation() {
    setNavigationOpen(false);
    requestAnimationFrame(() => menuButtonRef.current?.focus());
  }

  return (
    <div className="min-h-screen bg-canvas">
      <Sidebar open={navigationOpen} onClose={closeNavigation} />
      <div className="flex min-h-screen flex-col lg:pl-64">
        <TopContextBar menuButtonRef={menuButtonRef} navigationOpen={navigationOpen} page={page} scope={scope} onMenuToggle={() => setNavigationOpen((current) => !current)} />
        <WorkspaceContainer>{children}</WorkspaceContainer>
      </div>
    </div>
  );
}
