"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { RequireAuth } from "@/components/RequireAuth";
import { StatusBadge } from "@/components/StatusBadge";
import { api } from "@/lib/api";
import type { DashboardData } from "@/lib/types";

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="card p-5">
      <p className="text-sm text-ink-600">{label}</p>
      <p className="mt-1 text-3xl font-semibold text-ink-900">{value}</p>
    </div>
  );
}

function DashboardContent() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.get<DashboardData>("/api/dashboard"),
  });

  if (isLoading || !data) {
    return <div className="text-sm text-ink-600">Loading dashboard...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink-900">Dashboard</h1>
        <p className="mt-1 text-sm text-ink-600">An overview of your research workspace.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Papers" value={data.stats.paper_count} />
        <StatCard label="Experiments" value={data.stats.experiment_count} />
        <StatCard label="AI Insights" value={data.stats.ai_insight_count} />
        <StatCard label="Conversations" value={data.stats.conversation_count} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-semibold text-ink-900">Recent Papers</h2>
            <Link href="/papers" className="text-sm font-medium text-brand-600 hover:underline">
              View all
            </Link>
          </div>
          {data.recent_papers.length === 0 ? (
            <p className="text-sm text-ink-600">No papers uploaded yet.</p>
          ) : (
            <ul className="flex flex-col divide-y divide-slate-100">
              {data.recent_papers.map((p) => (
                <li key={p.id} className="flex items-center justify-between py-3">
                  <Link href={`/papers/${p.id}`} className="truncate text-sm font-medium text-ink-900 hover:text-brand-600">
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
            <h2 className="font-semibold text-ink-900">Recent Experiments</h2>
            <Link href="/experiments" className="text-sm font-medium text-brand-600 hover:underline">
              View all
            </Link>
          </div>
          {data.recent_experiments.length === 0 ? (
            <p className="text-sm text-ink-600">No experiments logged yet.</p>
          ) : (
            <ul className="flex flex-col divide-y divide-slate-100">
              {data.recent_experiments.map((e) => (
                <li key={e.id} className="py-3">
                  <Link href={`/experiments/${e.id}`} className="text-sm font-medium text-ink-900 hover:text-brand-600">
                    {e.name}
                  </Link>
                  <p className="text-xs text-ink-600">{e.model || "No model specified"}</p>
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
