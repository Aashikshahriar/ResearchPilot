"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/lib/api";

interface ConversationSummary {
  id: string;
  title: string | null;
  created_at: string;
}

export function AnalysisTab({ paperId }: { paperId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["conversations", paperId],
    queryFn: () => api.get<ConversationSummary[]>(`/api/papers/${paperId}/conversations`),
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="card p-5">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-ink-900 dark:text-slate-100">Compare with another paper</h2>
          <Link href={`/compare?a=${paperId}`} className="btn-secondary">
            Open comparison
          </Link>
        </div>
        <p className="mt-2 text-sm text-ink-600 dark:text-slate-400">
          Generate a structured, section-by-section comparison against another paper in your library.
        </p>
      </div>

      <div className="card p-5">
        <h2 className="mb-3 font-semibold text-ink-900 dark:text-slate-100">Conversation history</h2>
        {isLoading ? (
          <p className="text-sm text-ink-600 dark:text-slate-400">Loading conversations...</p>
        ) : !data || data.length === 0 ? (
          <EmptyState title="No conversations yet" description="Ask a question in the Chat tab to start one." />
        ) : (
          <ul className="flex flex-col divide-y divide-slate-100 dark:divide-ink-700">
            {data.map((c) => (
              <li key={c.id} className="py-3">
                <p className="text-sm font-medium text-ink-900 dark:text-slate-100">{c.title || "Untitled conversation"}</p>
                <p className="text-xs text-ink-600 dark:text-slate-400">{new Date(c.created_at).toLocaleString()}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
