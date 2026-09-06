"use client";

import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/EmptyState";
import { api, API_URL } from "@/lib/api";
import type { Figure } from "@/lib/types";

function toStaticUrl(imagePath: string): string {
  const marker = "storage/figures/";
  const idx = imagePath.replace(/\\/g, "/").indexOf(marker);
  const relative = idx >= 0 ? imagePath.replace(/\\/g, "/").slice(idx + marker.length) : imagePath;
  return `${API_URL}/static/figures/${relative}`;
}

const LABELS: Record<string, string> = {
  architecture_diagram: "Architecture Diagram",
  flowchart: "Flowchart",
  graph_plot: "Graph / Plot",
  table: "Table",
  microscopy_image: "Microscopy / Image",
  mathematical_figure: "Mathematical Figure",
  other: "Other",
};

export function FiguresTab({ paperId }: { paperId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["figures", paperId],
    queryFn: () => api.get<Figure[]>(`/api/papers/${paperId}/figures`),
  });

  if (isLoading) return <div className="text-sm text-ink-600 dark:text-slate-400">Loading figures...</div>;

  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="No figures detected"
        description="Figures are extracted and classified automatically once processing completes."
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      {data.map((fig, idx) => (
        <div key={fig.id} className="card overflow-hidden">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={toStaticUrl(fig.image_path)} alt={`Figure ${idx + 1}`} className="max-h-72 w-full bg-slate-50 object-contain dark:bg-ink-700" />
          <div className="p-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-ink-900 dark:text-slate-100">Figure {idx + 1}</h3>
              <span className="text-xs text-ink-600 dark:text-slate-400">p.{fig.page_number}</span>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="badge bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
                {fig.classification ? LABELS[fig.classification] ?? fig.classification : "Unclassified"}
              </span>
              {fig.confidence !== null && (
                <span className="text-ink-600 dark:text-slate-400">Confidence: {Math.round((fig.confidence ?? 0) * 100)}%</span>
              )}
            </div>
            <p className="mt-2 text-sm text-ink-700 dark:text-slate-300">{fig.description || "No description generated yet."}</p>
            {fig.vision_model && <p className="mt-2 text-xs text-ink-500 dark:text-slate-500">Model: {fig.vision_model}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}
