"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { RequireAuth } from "@/components/RequireAuth";
import { StatusBadge } from "@/components/StatusBadge";
import { OverviewTab } from "@/components/paper/OverviewTab";
import { ChatTab } from "@/components/paper/ChatTab";
import { FiguresTab } from "@/components/paper/FiguresTab";
import { AnalysisTab } from "@/components/paper/AnalysisTab";
import { NotesTab } from "@/components/paper/NotesTab";
import { api } from "@/lib/api";
import type { PaperDetail } from "@/lib/types";

const TABS = ["Overview", "Chat", "Figures", "Analysis", "Notes"] as const;
type Tab = (typeof TABS)[number];

function PaperDetailContent({ id }: { id: string }) {
  const [tab, setTab] = useState<Tab>("Overview");
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: paper, isLoading } = useQuery({
    queryKey: ["paper", id],
    queryFn: () => api.get<PaperDetail>(`/api/papers/${id}`),
    refetchInterval: (query) => {
      const p = query.state.data as PaperDetail | undefined;
      return p && (p.status === "uploaded" || p.status === "processing") ? 3000 : false;
    },
  });

  const deletePaper = useMutation({
    mutationFn: () => api.del(`/api/papers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["papers"] });
      router.push("/papers");
    },
  });

  if (isLoading || !paper) {
    return <div className="text-sm text-ink-600">Loading paper...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900">{paper.title || paper.filename}</h1>
          <div className="mt-2 flex items-center gap-3">
            <StatusBadge status={paper.status} />
            {paper.authors && paper.authors.length > 0 && (
              <span className="text-sm text-ink-600">{paper.authors.join(", ")}</span>
            )}
          </div>
        </div>
        <button
          className="btn-secondary text-red-600"
          onClick={() => {
            if (confirm("Delete this paper? This cannot be undone.")) deletePaper.mutate();
          }}
        >
          Delete paper
        </button>
      </div>

      {paper.status === "failed" && (
        <div className="card border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Processing failed: {paper.processing_error || "Unknown error."}
        </div>
      )}
      {(paper.status === "uploaded" || paper.status === "processing") && (
        <div className="card border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
          This paper is still being processed — sections, embeddings, and figures will appear shortly.
        </div>
      )}

      <div className="flex gap-1 border-b border-slate-200">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              "border-b-2 px-4 py-2 text-sm font-medium transition",
              tab === t ? "border-brand-500 text-brand-700" : "border-transparent text-ink-600 hover:text-ink-900"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <div>
        {tab === "Overview" && <OverviewTab paper={paper} />}
        {tab === "Chat" && <ChatTab paperId={paper.id} />}
        {tab === "Figures" && <FiguresTab paperId={paper.id} />}
        {tab === "Analysis" && <AnalysisTab paperId={paper.id} />}
        {tab === "Notes" && <NotesTab paperId={paper.id} />}
      </div>
    </div>
  );
}

export default function PaperDetailPage() {
  const params = useParams<{ id: string }>();
  return (
    <RequireAuth>
      <PaperDetailContent id={params.id} />
    </RequireAuth>
  );
}
