"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { RequireAuth } from "@/components/RequireAuth";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { api, ApiError } from "@/lib/api";
import type { PaperListItem } from "@/lib/types";

function UploadButton() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const upload = useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return api.upload<PaperListItem>("/api/papers", formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["papers"] });
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Upload failed."),
  });

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            setError(null);
            upload.mutate(file);
          }
          e.target.value = "";
        }}
      />
      <button className="btn-primary" onClick={() => inputRef.current?.click()} disabled={upload.isPending}>
        {upload.isPending ? "Uploading..." : "Upload paper"}
      </button>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}

function PapersContent() {
  const { data, isLoading } = useQuery({
    queryKey: ["papers"],
    queryFn: () => api.get<PaperListItem[]>("/api/papers"),
    refetchInterval: (query) => {
      const papers = query.state.data as PaperListItem[] | undefined;
      const hasActive = papers?.some((p) => p.status === "uploaded" || p.status === "processing");
      return hasActive ? 3000 : false;
    },
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900">Papers</h1>
          <p className="mt-1 text-sm text-ink-600">Upload and manage your research library.</p>
        </div>
        <UploadButton />
      </div>

      {isLoading ? (
        <div className="text-sm text-ink-600">Loading papers...</div>
      ) : !data || data.length === 0 ? (
        <EmptyState
          title="No papers yet"
          description="Upload your first PDF to start extracting sections, generating embeddings, and chatting with it."
        />
      ) : (
        <div className="card divide-y divide-slate-100">
          {data.map((p) => (
            <Link
              key={p.id}
              href={`/papers/${p.id}`}
              className="flex items-center justify-between gap-4 px-5 py-4 transition hover:bg-slate-50"
            >
              <div className="min-w-0">
                <p className="truncate font-medium text-ink-900">{p.title || p.filename}</p>
                <p className="text-xs text-ink-600">
                  {p.page_count ? `${p.page_count} pages` : "Processing..."} &middot;{" "}
                  {new Date(p.created_at).toLocaleDateString()}
                </p>
              </div>
              <StatusBadge status={p.status} />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PapersPage() {
  return (
    <RequireAuth>
      <PapersContent />
    </RequireAuth>
  );
}
