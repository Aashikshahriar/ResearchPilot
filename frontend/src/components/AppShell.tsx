"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode, useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import clsx from "clsx";
import { useAuth } from "@/lib/auth-context";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/papers", label: "Papers" },
  { href: "/experiments", label: "Experiments" },
  { href: "/compare", label: "Compare" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const router = useRouter();
  const [query, setQuery] = useState("");

  function onSearch(e: FormEvent) {
    e.preventDefault();
    if (query.trim()) router.push(`/search?q=${encodeURIComponent(query.trim())}`);
  }

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white p-6 md:flex md:flex-col">
        <Link href="/dashboard" className="mb-8 flex items-center gap-2 text-lg font-semibold text-ink-900">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500 text-white">R</span>
          ResearchPilot
        </Link>
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "rounded-lg px-3 py-2 text-sm font-medium transition",
                pathname?.startsWith(item.href) ? "bg-brand-50 text-brand-700" : "text-ink-700 hover:bg-slate-50"
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto pt-6">
          <div className="mb-2 truncate text-xs text-ink-600">{user?.email}</div>
          <button onClick={logout} className="btn-secondary w-full">
            Sign out
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-4 border-b border-slate-200 bg-white px-6 py-4">
          <form onSubmit={onSearch} className="flex-1">
            <input
              className="input max-w-md"
              placeholder="Search papers, chunks, experiments..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </form>
        </header>
        <main className="flex-1 bg-slate-50 p-6">{children}</main>
      </div>
    </div>
  );
}
