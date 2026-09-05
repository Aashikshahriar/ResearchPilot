"use client";

import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { RequireAuth } from "@/components/RequireAuth";
import { api, ApiError } from "@/lib/api";
import type { ComparisonResult, PaperListItem } from "@/lib/types";

const FIELDS: { key: keyof ComparisonResult; label: string }[] = [
  { key: "research_problem", label: "Research Problem" },
  { key: "methodology", label: "Methodology" },
  { key: "datasets", label: "Datasets" },
  { key: "models", label: "Models" },
  { key: "results", label: "Results" },
  { key: "strengths", label: "Strengths" },
  { key: "limitations", label: "Limitations" },
  { key: "key_differences", label: "Key Differences" },
];

function CompareContent() {
  const searchParams = useSearchParams();
  const { data: papers } = useQuery({ queryKey: ["papers"], queryFn: () => api.get<PaperListItem[]>("/api/papers") });
  const [paperA, setPaperA] = useState(searchParams.get("a") || "");
  const [paperB, setPaperB] = useState("");
  const [error, setError] = useState<string | null>(null);

  const compare = useMutation({
    mutationFn: () => api.post<{ comparison: ComparisonResult }>("/api/papers/compare", { paper_ids: [paperA, paperB] }),
    onError: (err) => setError(err instanceof ApiError ? err.message : "Comparison failed."),
  });

  function run() {
    setError(null);
    if (!paperA || !paperB || paperA === paperB) {
      setError("Select two different papers to compare.");
      return;
    }
    compare.mutate();
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink-900">Compare Papers</h1>
        <p className="mt-1 text-sm text-ink-600">Select two papers to generate a structured, side-by-side comparison.</p>
      </div>

      <div className="card grid grid-cols-1 gap-4 p-5 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-ink-800">Paper A</label>
          <select className="input" value={paperA} onChange={(e) => setPaperA(e.target.value)}>
            <option value="">Select a paper...</option>
            {papers?.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title || p.filename}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-ink-800">Paper B</label>
          <select className="input" value={paperB} onChange={(e) => setPaperB(e.target.value)}>
            <option value="">Select a paper...</option>
            {papers?.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title || p.filename}
              </option>
            ))}
          </select>
        </div>
        <div className="sm:col-span-2">
          <button className="btn-primary" onClick={run} disabled={compare.isPending}>
            {compare.isPending ? "Comparing..." : "Compare"}
          </button>
          {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        </div>
      </div>

      {compare.data && (
        <div className="grid grid-cols-1 gap-4">
          {FIELDS.map((f) => (
            <div key={f.key} className="card p-5">
              <h2 className="font-semibold text-ink-900">{f.label}</h2>
              <p className="mt-2 whitespace-pre-line text-sm text-ink-700">{compare.data.comparison[f.key]}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ComparePage() {
  return (
    <RequireAuth>
      <CompareContent />
    </RequireAuth>
  );
}
