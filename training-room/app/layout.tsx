import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Training Room • Real-Time AI Benchmark & Model Telemetry",
  description: "Autonomous training room monitoring real-time model training and 12-parameter frontier benchmark growth.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 min-h-screen">
        {children}
      </body>
    </html>
  );
}
