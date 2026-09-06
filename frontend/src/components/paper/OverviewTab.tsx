"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { PaperDetail } from "@/lib/types";

export function OverviewTab({ paper }: { paper: PaperDetail }) {
  const queryClient = useQueryClient();
  const summarize = useMutation({
    mutationFn: () => api.post(`/api/papers/${paper.id}/summarize`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["paper", paper.id] }),
  });

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <div className="card p-5 lg:col-span-2">
        <h2 className="font-semibold text-ink-900 dark:text-slate-100">Abstract</h2>
        <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink-700 dark:text-slate-300">
          {paper.abstract || "No abstract could be extracted from this paper."}
        </p>

        <div className="mt-6 flex items-center justify-between">
          <h2 className="font-semibold text-ink-900 dark:text-slate-100">AI Summary</h2>
          <button className="btn-secondary" onClick={() => summarize.mutate()} disabled={summarize.isPending}>
            {summarize.isPending ? "Summarizing..." : paper.ai_summary ? "Regenerate" : "Generate summary"}
          </button>
        </div>
        <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink-700 dark:text-slate-300">
          {paper.ai_summary || "No AI summary generated yet."}
        </p>
      </div>

      <div className="card p-5">
        <h2 className="font-semibold text-ink-900 dark:text-slate-100">Metadata</h2>
        <dl className="mt-3 flex flex-col gap-3 text-sm">
          <div>
            <dt className="text-ink-600 dark:text-slate-400">Authors</dt>
            <dd className="text-ink-900 dark:text-slate-100">{paper.authors?.length ? paper.authors.join(", ") : "Unknown"}</dd>
          </div>
          <div>
            <dt className="text-ink-600 dark:text-slate-400">Pages</dt>
            <dd className="text-ink-900 dark:text-slate-100">{paper.page_count ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-ink-600 dark:text-slate-400">File size</dt>
            <dd className="text-ink-900 dark:text-slate-100">{(paper.file_size_bytes / 1024 / 1024).toFixed(2)} MB</dd>
          </div>
          <div>
            <dt className="text-ink-600 dark:text-slate-400">Uploaded</dt>
            <dd className="text-ink-900 dark:text-slate-100">{new Date(paper.created_at).toLocaleString()}</dd>
          </div>
        </dl>
      </div>

      <div className="card p-5 lg:col-span-3">
        <h2 className="mb-3 font-semibold text-ink-900 dark:text-slate-100">Sections ({paper.sections.length})</h2>
        {paper.sections.length === 0 ? (
          <p className="text-sm text-ink-600 dark:text-slate-400">Sections will appear here once processing completes.</p>
        ) : (
          <div className="flex flex-col divide-y divide-slate-100 dark:divide-ink-700">
            {paper.sections.map((s) => (
              <details key={s.id} className="group py-3">
                <summary className="cursor-pointer list-none text-sm font-medium text-ink-900 dark:text-slate-100">
                  {s.order_index + 1}. {s.title}
                  {s.page_start && <span className="ml-2 text-xs font-normal text-ink-600 dark:text-slate-400">p.{s.page_start}-{s.page_end}</span>}
                </summary>
                <p className="mt-2 whitespace-pre-line text-sm text-ink-700 dark:text-slate-300">{s.content.slice(0, 1200)}</p>
              </details>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
