"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { RequireAuth } from "@/components/RequireAuth";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/lib/api";
import type { SearchResultItem } from "@/lib/types";

const TYPE_LABELS: Record<string, string> = { paper: "Paper", chunk: "Excerpt", experiment: "Experiment" };

function SearchContent() {
  const params = useSearchParams();
  const q = params.get("q") || "";

  const { data, isLoading } = useQuery({
    queryKey: ["search", q],
    queryFn: () => api.get<SearchResultItem[]>(`/api/search?q=${encodeURIComponent(q)}`),
    enabled: q.length >= 2,
  });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink-900">Search results for &ldquo;{q}&rdquo;</h1>
      </div>

      {isLoading ? (
        <div className="text-sm text-ink-600">Searching...</div>
      ) : !data || data.length === 0 ? (
        <EmptyState title="No results found" description="Try a different search term." />
      ) : (
        <div className="card divide-y divide-slate-100">
          {data.map((r) => (
            <Link
              key={`${r.type}-${r.id}`}
              href={r.paper_id ? `/papers/${r.paper_id}` : "#"}
              className="flex flex-col gap-1 px-5 py-4 hover:bg-slate-50"
            >
              <div className="flex items-center gap-2">
                <span className="badge bg-brand-50 text-brand-700">{TYPE_LABELS[r.type]}</span>
                <span className="font-medium text-ink-900">{r.title}</span>
              </div>
              {r.snippet && <p className="text-sm text-ink-600">{r.snippet}</p>}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <RequireAuth>
      <SearchContent />
    </RequireAuth>
  );
}
