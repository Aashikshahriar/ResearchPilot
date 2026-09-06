"use client";

import { FormEvent, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { RequireAuth } from "@/components/RequireAuth";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/lib/api";
import type { Experiment, Metric } from "@/lib/types";

const CHART_COLORS = ["#4a63ee", "#16a34a", "#ea580c", "#9333ea", "#0ea5e9"];

function AddMetricForm({ experimentId }: { experimentId: string }) {
  const [name, setName] = useState("");
  const [value, setValue] = useState("");
  const [step, setStep] = useState("");
  const queryClient = useQueryClient();

  const addMetric = useMutation({
    mutationFn: () =>
      api.post(`/api/experiments/${experimentId}/metrics`, {
        name,
        value: parseFloat(value),
        step: step ? parseInt(step) : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["metrics", experimentId] });
      setName("");
      setValue("");
      setStep("");
    },
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (name.trim() && value.trim()) addMetric.mutate();
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-wrap items-end gap-3">
      <div>
        <label className="mb-1 block text-xs font-medium text-ink-800 dark:text-slate-300">Metric name</label>
        <input className="input w-40" placeholder="accuracy" value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-xs font-medium text-ink-800 dark:text-slate-300">Value</label>
        <input className="input w-28" type="number" step="any" value={value} onChange={(e) => setValue(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-xs font-medium text-ink-800 dark:text-slate-300">Step</label>
        <input className="input w-24" type="number" value={step} onChange={(e) => setStep(e.target.value)} />
      </div>
      <button className="btn-primary" type="submit" disabled={addMetric.isPending}>
        Add metric
      </button>
    </form>
  );
}

function MetricsChart({ metrics }: { metrics: Metric[] }) {
  const { series, points } = useMemo(() => {
    const names = Array.from(new Set(metrics.map((m) => m.name)));
    const byStep = new Map<number, Record<string, number | string>>();
    metrics.forEach((m, idx) => {
      const step = m.step ?? idx;
      const row = byStep.get(step) || { step };
      row[m.name] = m.value;
      byStep.set(step, row);
    });
    return { series: names, points: Array.from(byStep.values()).sort((a, b) => (a.step as number) - (b.step as number)) };
  }, [metrics]);

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={points}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="step" stroke="#64748b" fontSize={12} />
        <YAxis stroke="#64748b" fontSize={12} />
        <Tooltip />
        <Legend />
        {series.map((name, idx) => (
          <Line key={name} type="monotone" dataKey={name} stroke={CHART_COLORS[idx % CHART_COLORS.length]} strokeWidth={2} dot={false} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

function ExperimentDetailContent({ id }: { id: string }) {
  const { data: experiment } = useQuery({
    queryKey: ["experiment", id],
    queryFn: () => api.get<Experiment>(`/api/experiments/${id}`),
  });
  const { data: metrics, isLoading } = useQuery({
    queryKey: ["metrics", id],
    queryFn: () => api.get<Metric[]>(`/api/experiments/${id}/metrics`),
  });

  if (!experiment) return <div className="text-sm text-ink-600 dark:text-slate-400">Loading experiment...</div>;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink-900 dark:text-slate-100">{experiment.name}</h1>
        <p className="mt-1 text-sm text-ink-600 dark:text-slate-400">
          {[experiment.model, experiment.dataset].filter(Boolean).join(" · ") || "No model/dataset specified"}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="card p-4">
          <p className="text-xs text-ink-600 dark:text-slate-400">Learning rate</p>
          <p className="text-lg font-semibold text-ink-900 dark:text-slate-100">{experiment.learning_rate ?? "—"}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-ink-600 dark:text-slate-400">Batch size</p>
          <p className="text-lg font-semibold text-ink-900 dark:text-slate-100">{experiment.batch_size ?? "—"}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-ink-600 dark:text-slate-400">Epochs</p>
          <p className="text-lg font-semibold text-ink-900 dark:text-slate-100">{experiment.epochs ?? "—"}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-ink-600 dark:text-slate-400">Logged metrics</p>
          <p className="text-lg font-semibold text-ink-900 dark:text-slate-100">{metrics?.length ?? 0}</p>
        </div>
      </div>

      {experiment.notes && (
        <div className="card p-5">
          <h2 className="font-semibold text-ink-900 dark:text-slate-100">Notes</h2>
          <p className="mt-2 whitespace-pre-line text-sm text-ink-700 dark:text-slate-300">{experiment.notes}</p>
        </div>
      )}

      <div className="card p-5">
        <h2 className="mb-4 font-semibold text-ink-900 dark:text-slate-100">Metrics over time</h2>
        {isLoading ? (
          <p className="text-sm text-ink-600 dark:text-slate-400">Loading metrics...</p>
        ) : !metrics || metrics.length === 0 ? (
          <EmptyState title="No metrics logged yet" description="Add a metric below to see it charted here." />
        ) : (
          <MetricsChart metrics={metrics} />
        )}
        <div className="mt-4 border-t border-slate-100 pt-4">
          <AddMetricForm experimentId={id} />
        </div>
      </div>
    </div>
  );
}

export default function ExperimentDetailPage() {
  const params = useParams<{ id: string }>();
  return (
    <RequireAuth>
      <ExperimentDetailContent id={params.id} />
    </RequireAuth>
  );
}
