"use client";

import { useTheme } from "@/lib/theme-context";
import { useLanguage } from "@/lib/language-context";

export function ThemeLangToggle({ className }: { className?: string }) {
  const { theme, toggleTheme } = useTheme();
  const { language, setLanguage } = useLanguage();

  return (
    <div className={className ?? "flex items-center gap-2"}>
      <div className="flex overflow-hidden rounded-lg border border-slate-300 text-xs font-medium dark:border-ink-600">
        <button
          onClick={() => setLanguage("en")}
          className={
            language === "en"
              ? "bg-brand-500 px-2.5 py-1.5 text-white"
              : "bg-white px-2.5 py-1.5 text-ink-700 hover:bg-slate-50 dark:bg-ink-800 dark:text-slate-300 dark:hover:bg-ink-700"
          }
          aria-pressed={language === "en"}
        >
          EN
        </button>
        <button
          onClick={() => setLanguage("bn")}
          className={
            language === "bn"
              ? "bg-brand-500 px-2.5 py-1.5 text-white"
              : "bg-white px-2.5 py-1.5 text-ink-700 hover:bg-slate-50 dark:bg-ink-800 dark:text-slate-300 dark:hover:bg-ink-700"
          }
          aria-pressed={language === "bn"}
        >
          বাং
        </button>
      </div>
      <button
        onClick={toggleTheme}
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 bg-white text-sm transition hover:bg-slate-50 dark:border-ink-600 dark:bg-ink-800 dark:hover:bg-ink-700"
        aria-label="Toggle theme"
        title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
      >
        {theme === "light" ? "🌙" : "☀️"}
      </button>
    </div>
  );
}
