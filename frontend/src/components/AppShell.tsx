"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode, useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import clsx from "clsx";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/language-context";
import { ThemeLangToggle } from "./ThemeLangToggle";
import type { TranslationKey } from "@/lib/translations";

const NAV_ITEMS: { href: string; labelKey: TranslationKey; dot: string }[] = [
  { href: "/dashboard", labelKey: "nav_dashboard", dot: "bg-brand-500" },
  { href: "/papers", labelKey: "nav_papers", dot: "bg-teal-500" },
  { href: "/experiments", labelKey: "nav_experiments", dot: "bg-amber-500" },
  { href: "/compare", labelKey: "nav_compare", dot: "bg-accent-500" },
  { href: "/board", labelKey: "nav_board", dot: "bg-rose-500" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const router = useRouter();
  const [query, setQuery] = useState("");

  function onSearch(e: FormEvent) {
    e.preventDefault();
    if (query.trim()) router.push(`/search?q=${encodeURIComponent(query.trim())}`);
  }

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-ink-900">
      <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white p-6 dark:border-ink-700 dark:bg-ink-800 md:flex md:flex-col">
        <Link href="/dashboard" className="mb-8 flex items-center gap-2 text-lg font-semibold text-ink-900 dark:text-slate-100">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 text-white">
            R
          </span>
          {t("appName")}
        </Link>
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition",
                pathname?.startsWith(item.href)
                  ? "bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300"
                  : "text-ink-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-ink-700"
              )}
            >
              <span className={clsx("h-1.5 w-1.5 rounded-full", item.dot)} />
              {t(item.labelKey)}
            </Link>
          ))}
        </nav>
        <div className="mt-auto flex flex-col gap-4 pt-6">
          <ThemeLangToggle />
          <div>
            <div className="mb-2 truncate text-xs text-ink-600 dark:text-slate-400">{user?.email}</div>
            <button onClick={logout} className="btn-secondary w-full">
              {t("signOut")}
            </button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-4 border-b border-slate-200 bg-white px-6 py-4 dark:border-ink-700 dark:bg-ink-800">
          <form onSubmit={onSearch} className="flex-1">
            <input
              className="input max-w-md"
              placeholder={t("searchPlaceholder")}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </form>
          <div className="md:hidden">
            <ThemeLangToggle />
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
