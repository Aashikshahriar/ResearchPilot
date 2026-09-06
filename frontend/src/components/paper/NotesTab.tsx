"use client";

import { useEffect, useState } from "react";

export function NotesTab({ paperId }: { paperId: string }) {
  const storageKey = `rp_notes_${paperId}`;
  const [notes, setNotes] = useState("");
  const [savedAt, setSavedAt] = useState<Date | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem(storageKey);
    if (stored) setNotes(stored);
  }, [storageKey]);

  function save() {
    localStorage.setItem(storageKey, notes);
    setSavedAt(new Date());
  }

  return (
    <div className="card p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-semibold text-ink-900 dark:text-slate-100">Your notes</h2>
        <div className="flex items-center gap-3">
          {savedAt && <span className="text-xs text-ink-600 dark:text-slate-400">Saved {savedAt.toLocaleTimeString()}</span>}
          <button className="btn-secondary" onClick={save}>
            Save
          </button>
        </div>
      </div>
      <textarea
        className="input min-h-[50vh] resize-y font-mono text-sm"
        placeholder="Jot down your own thoughts, follow-up questions, or ideas about this paper..."
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
      />
      <p className="mt-2 text-xs text-ink-500 dark:text-slate-500">Notes are stored locally in your browser for this paper.</p>
    </div>
  );
}
