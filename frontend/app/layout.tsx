import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/Providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "ExecutiveAI - Analytics Platform",
    template: "%s | ExecutiveAI",
  },
  description:
    "Enterprise-grade executive analytics platform powered by AI. Real-time insights, forecasting, and intelligent business intelligence.",
  keywords: ["analytics", "executive", "AI", "business intelligence", "forecasting"],
  authors: [{ name: "ExecutiveAI" }],
  creator: "ExecutiveAI",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
