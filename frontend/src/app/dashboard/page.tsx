"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { RequireAuth } from "@/components/RequireAuth";
import { StatusBadge } from "@/components/StatusBadge";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/language-context";
import { exportDashboardPdf } from "@/lib/export-pdf";
import { api } from "@/lib/api";
import type { DashboardData } from "@/lib/types";

const STAT_STYLES = [
  { ring: "from-brand-500 to-brand-400", text: "text-brand-600 dark:text-brand-400" },
  { ring: "from-amber-500 to-amber-400", text: "text-amber-600 dark:text-amber-400" },
  { ring: "from-accent-500 to-accent-400", text: "text-accent-600 dark:text-accent-400" },
  { ring: "from-teal-500 to-teal-400", text: "text-teal-600 dark:text-teal-400" },
];

function StatCard({ label, value, style }: { label: string; value: number; style: (typeof STAT_STYLES)[number] }) {
  return (
    <div className="card overflow-hidden p-5">
      <div className={`mb-3 h-1.5 w-10 rounded-full bg-gradient-to-r ${style.ring}`} />
      <p className="text-sm text-ink-600 dark:text-slate-400">{label}</p>
      <p className={`mt-1 text-3xl font-semibold ${style.text}`}>{value}</p>
    </div>
  );
}

function DashboardContent() {
  const { t } = useLanguage();
  const { user } = useAuth();
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.get<DashboardData>("/api/dashboard"),
  });

  if (isLoading || !data) {
    return <div className="text-sm text-ink-600 dark:text-slate-400">{t("dashboard_loading")}</div>;
  }

  const stats = [
    { label: t("dashboard_papers"), value: data.stats.paper_count },
    { label: t("dashboard_experiments"), value: data.stats.experiment_count },
    { label: t("dashboard_insights"), value: data.stats.ai_insight_count },
    { label: t("dashboard_conversations"), value: data.stats.conversation_count },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900 dark:text-slate-100">{t("dashboard_title")}</h1>
          <p className="mt-1 text-sm text-ink-600 dark:text-slate-400">{t("dashboard_subtitle")}</p>
        </div>
        <button className="btn-secondary" onClick={() => exportDashboardPdf(data, user?.email)}>
          {t("dashboard_downloadPdf")}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {stats.map((s, idx) => (
          <StatCard key={s.label} label={s.label} value={s.value} style={STAT_STYLES[idx % STAT_STYLES.length]} />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-semibold text-ink-900 dark:text-slate-100">{t("dashboard_recentPapers")}</h2>
            <Link href="/papers" className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400">
              {t("dashboard_viewAll")}
            </Link>
          </div>
          {data.recent_papers.length === 0 ? (
            <p className="text-sm text-ink-600 dark:text-slate-400">{t("dashboard_noPapers")}</p>
          ) : (
            <ul className="flex flex-col divide-y divide-slate-100 dark:divide-ink-700">
              {data.recent_papers.map((p) => (
                <li key={p.id} className="flex items-center justify-between py-3">
                  <Link
                    href={`/papers/${p.id}`}
                    className="truncate text-sm font-medium text-ink-900 hover:text-brand-600 dark:text-slate-100 dark:hover:text-brand-400"
                  >
                    {p.title || p.filename}
                  </Link>
                  <StatusBadge status={p.status} />
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-semibold text-ink-900 dark:text-slate-100">{t("dashboard_recentExperiments")}</h2>
            <Link href="/experiments" className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400">
              {t("dashboard_viewAll")}
            </Link>
          </div>
          {data.recent_experiments.length === 0 ? (
            <p className="text-sm text-ink-600 dark:text-slate-400">{t("dashboard_noExperiments")}</p>
          ) : (
            <ul className="flex flex-col divide-y divide-slate-100 dark:divide-ink-700">
              {data.recent_experiments.map((e) => (
                <li key={e.id} className="py-3">
                  <Link
                    href={`/experiments/${e.id}`}
                    className="text-sm font-medium text-ink-900 hover:text-brand-600 dark:text-slate-100 dark:hover:text-brand-400"
                  >
                    {e.name}
                  </Link>
                  <p className="text-xs text-ink-600 dark:text-slate-400">{e.model || "No model specified"}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <RequireAuth>
      <DashboardContent />
    </RequireAuth>
  );
}
