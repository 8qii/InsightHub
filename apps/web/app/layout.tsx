import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InsightHub | Enterprise AI Analyst",
  description: "Traceable answers across business knowledge and data.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
