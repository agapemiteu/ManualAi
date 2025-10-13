import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { MessageCircle, Upload } from "lucide-react";
import clsx from "clsx";

export const metadata: Metadata = {
  title: "ManualAi - AI-Powered Car Manual Assistant",
  description: "Chat with your car manuals using AI. Upload any manual and get instant, intelligent answers to your questions.",
};

const navLinkClass = "inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="bg-slate-900">
      <body className="min-h-screen bg-slate-900 text-slate-100 antialiased">
        <div className="flex min-h-screen flex-col">
          <header className="border-b border-slate-800 bg-slate-950/70 backdrop-blur">
            <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
              <Link href="/" className="flex items-center gap-3 text-lg font-semibold text-white">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-blue-600">
                  <MessageCircle className="h-5 w-5 text-white" />
                </div>
                <span className="bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent">ManualAi</span>
              </Link>
              <nav className="flex items-center gap-2">
                <Link
                  href="/"
                  className={clsx(navLinkClass, "hover:bg-slate-800/70 text-slate-200")}
                >
                  <MessageCircle className="h-4 w-4" />
                  Chat
                </Link>
                <Link
                  href="/upload"
                  className={clsx(navLinkClass, "bg-sky-600 text-white hover:bg-sky-500")}
                >
                  <Upload className="h-4 w-4" />
                  Upload Manual
                </Link>
              </nav>
            </div>
          </header>
          <main className="flex-1">{children}</main>
          <footer className="border-t border-slate-800 bg-slate-950/70 py-4 text-center text-xs text-slate-500">
            <p>Powered by AI • <span className="text-sky-400">ManualAi</span> © 2025 • Max upload: 20MB</p>
          </footer>
        </div>
      </body>
    </html>
  );
}
