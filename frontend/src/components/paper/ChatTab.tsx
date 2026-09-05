"use client";

import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import type { ChatResponse, Citation } from "@/lib/types";

interface DisplayMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

export function ChatTab({ paperId }: { paperId: string }) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string | null>(null);

  const chat = useMutation({
    mutationFn: (q: string) =>
      api.post<ChatResponse>(`/api/papers/${paperId}/chat`, { question: q, conversation_id: conversationId }),
    onSuccess: (res) => {
      setConversationId(res.conversation_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.answer, citations: res.citations }]);
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to get a response."),
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setQuestion("");
    chat.mutate(trimmed);
  }

  return (
    <div className="card flex h-[70vh] flex-col p-5">
      <div className="flex-1 space-y-4 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <p className="text-sm text-ink-600">
            Ask a question about this paper, e.g. &ldquo;What is the main contribution?&rdquo; Answers are grounded
            in retrieved excerpts from the paper.
          </p>
        )}
        {messages.map((m, idx) => (
          <div key={idx} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
            <div
              className={
                m.role === "user"
                  ? "max-w-[80%] rounded-2xl rounded-br-sm bg-brand-500 px-4 py-2.5 text-sm text-white"
                  : "max-w-[80%] rounded-2xl rounded-bl-sm bg-slate-100 px-4 py-2.5 text-sm text-ink-900"
              }
            >
              <p className="whitespace-pre-line">{m.content}</p>
              {m.citations && m.citations.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {m.citations.map((c) => (
                    <span key={c.chunk_id} className="badge bg-white/70 text-brand-700" title={c.excerpt}>
                      [{c.section_title}]
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {chat.isPending && <p className="text-sm text-ink-600">Thinking...</p>}
      </div>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      <form onSubmit={onSubmit} className="mt-4 flex gap-2 border-t border-slate-100 pt-4">
        <input
          className="input"
          placeholder="Ask a question about this paper..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button className="btn-primary" type="submit" disabled={chat.isPending}>
          Send
        </button>
      </form>
    </div>
  );
}
