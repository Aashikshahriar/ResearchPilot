"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { RequireAuth } from "@/components/RequireAuth";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/lib/api";
import type { Experiment } from "@/lib/types";

function NewExperimentForm({ onDone }: { onDone: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [model, setModel] = useState("");
  const [dataset, setDataset] = useState("");
  const [learningRate, setLearningRate] = useState("");
  const [batchSize, setBatchSize] = useState("");
  const [epochs, setEpochs] = useState("");
  const [notes, setNotes] = useState("");
  const queryClient = useQueryClient();

  const create = useMutation({
    mutationFn: () =>
      api.post("/api/experiments", {
        name,
        model: model || null,
        dataset: dataset || null,
        learning_rate: learningRate ? parseFloat(learningRate) : null,
        batch_size: batchSize ? parseInt(batchSize) : null,
        epochs: epochs ? parseInt(epochs) : null,
        notes: notes || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["experiments"] });
      setOpen(false);
      setName("");
      setModel("");
      setDataset("");
      setLearningRate("");
      setBatchSize("");
      setEpochs("");
      setNotes("");
      onDone();
    },
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (name.trim()) create.mutate();
  }

  if (!open) {
    return (
      <button className="btn-primary" onClick={() => setOpen(true)}>
        New experiment
      </button>
    );
  }

  return (
    <form onSubmit={onSubmit} className="card grid grid-cols-1 gap-3 p-5 sm:grid-cols-2">
      <div className="sm:col-span-2">
        <label className="mb-1 block text-sm font-medium text-ink-800">Name</label>
        <input className="input" required value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-ink-800">Model</label>
        <input className="input" value={model} onChange={(e) => setModel(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-ink-800">Dataset</label>
        <input className="input" value={dataset} onChange={(e) => setDataset(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-ink-800">Learning rate</label>
        <input className="input" type="number" step="any" value={learningRate} onChange={(e) => setLearningRate(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-ink-800">Batch size</label>
        <input className="input" type="number" value={batchSize} onChange={(e) => setBatchSize(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-ink-800">Epochs</label>
        <input className="input" type="number" value={epochs} onChange={(e) => setEpochs(e.target.value)} />
      </div>
      <div className="sm:col-span-2">
        <label className="mb-1 block text-sm font-medium text-ink-800">Notes</label>
        <textarea className="input" value={notes} onChange={(e) => setNotes(e.target.value)} />
      </div>
      <div className="flex gap-2 sm:col-span-2">
        <button className="btn-primary" type="submit" disabled={create.isPending}>
          {create.isPending ? "Creating..." : "Create experiment"}
        </button>
        <button className="btn-secondary" type="button" onClick={() => setOpen(false)}>
          Cancel
        </button>
      </div>
    </form>
  );
}

function ExperimentsContent() {
  const { data, isLoading } = useQuery({ queryKey: ["experiments"], queryFn: () => api.get<Experiment[]>("/api/experiments") });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900">Experiments</h1>
          <p className="mt-1 text-sm text-ink-600">Track models, hyperparameters, and metrics.</p>
        </div>
      </div>

      <NewExperimentForm onDone={() => {}} />

      {isLoading ? (
        <div className="text-sm text-ink-600">Loading experiments...</div>
      ) : !data || data.length === 0 ? (
        <EmptyState title="No experiments yet" description="Create one above to start tracking metrics." />
      ) : (
        <div className="card divide-y divide-slate-100">
          {data.map((e) => (
            <Link key={e.id} href={`/experiments/${e.id}`} className="flex items-center justify-between px-5 py-4 hover:bg-slate-50">
              <div>
                <p className="font-medium text-ink-900">{e.name}</p>
                <p className="text-xs text-ink-600">
                  {[e.model, e.dataset].filter(Boolean).join(" · ") || "No model/dataset specified"}
                </p>
              </div>
              <span className="text-xs text-ink-600">{new Date(e.created_at).toLocaleDateString()}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ExperimentsPage() {
  return (
    <RequireAuth>
      <ExperimentsContent />
    </RequireAuth>
  );
}
