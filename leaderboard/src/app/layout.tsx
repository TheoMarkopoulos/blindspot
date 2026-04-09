import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BlindSpot Leaderboard",
  description: "LLM over-refusal evaluation leaderboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0a0a0f]">{children}</body>
    </html>
  );
}
