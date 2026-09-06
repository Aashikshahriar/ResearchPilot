"use client";

import Link from "next/link";
import { useLanguage } from "@/lib/language-context";
import { ThemeLangToggle } from "@/components/ThemeLangToggle";

const FEATURES = [
  {
    title: "Grounded RAG chat",
    description: "Ask questions about any uploaded paper and get answers retrieved and cited from the actual text — not hallucinated.",
    color: "from-brand-500 to-brand-400",
  },
  {
    title: "Figure understanding",
    description: "Every extracted figure is classified (architecture diagram, plot, table, and more) and described automatically.",
    color: "from-accent-500 to-accent-400",
  },
  {
    title: "Structured comparison",
    description: "Compare two or more papers side by side across methodology, datasets, results, and limitations.",
    color: "from-teal-500 to-teal-400",
  },
  {
    title: "Experiment tracking",
    description: "Log models, hyperparameters, and metrics for your own experiments, and visualize progress over time.",
    color: "from-amber-500 to-amber-400",
  },
  {
    title: "Full-text research search",
    description: "Search across every paper, chunk, and experiment in your personal workspace in one place.",
    color: "from-rose-500 to-rose-400",
  },
  {
    title: "Built for real pipelines",
    description: "Async background processing, pgvector-backed retrieval, and swappable LLM/vision providers under the hood.",
    color: "from-brand-500 via-accent-500 to-teal-500",
  },
];

export default function LandingPage() {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-white dark:bg-ink-900">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2 text-lg font-semibold text-ink-900 dark:text-slate-100">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 text-white">
            R
          </span>
          {t("appName")}
        </div>
        <nav className="flex items-center gap-3">
          <ThemeLangToggle />
          <Link href="/login" className="btn-secondary">
            {t("login")}
          </Link>
          <Link href="/register" className="btn-primary">
            {t("getStarted")}
          </Link>
        </nav>
      </header>

      <section className="relative overflow-hidden bg-hero-glow">
        <div className="mx-auto max-w-4xl px-6 pb-20 pt-16 text-center">
          <span className="badge mb-6 bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
            {t("landing_badge")}
          </span>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900 dark:text-slate-100 sm:text-5xl">
            {t("landing_title")}
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-ink-600 dark:text-slate-400">{t("landing_subtitle")}</p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link href="/register" className="btn-primary px-6 py-3 text-base">
              {t("landing_cta_primary")}
            </Link>
            <Link href="/login" className="btn-secondary px-6 py-3 text-base">
              {t("landing_cta_secondary")}
            </Link>
          </div>
        </div>
      </section>

      <section className="border-t border-slate-100 bg-slate-50 py-16 dark:border-ink-700 dark:bg-ink-800">
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="card overflow-hidden p-6">
              <div className={`mb-3 h-1.5 w-10 rounded-full bg-gradient-to-r ${f.color}`} />
              <h3 className="font-semibold text-ink-900 dark:text-slate-100">{f.title}</h3>
              <p className="mt-2 text-sm text-ink-600 dark:text-slate-400">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-slate-100 py-8 text-center text-sm text-ink-600 dark:border-ink-700 dark:text-slate-400">
        {t("footer")}
      </footer>
    </div>
  );
}
