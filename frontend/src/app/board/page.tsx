"use client";

import { DragEvent, FormEvent, useEffect, useState } from "react";
import { RequireAuth } from "@/components/RequireAuth";
import { useLanguage } from "@/lib/language-context";
import { ALL_PHASES, BoardCard, BoardColumnId, colorForPhase, getDefaultBoard } from "@/lib/board-data";

const STORAGE_KEY = "rp_kanban_board_v1";

const COLUMNS: { id: BoardColumnId; labelKey: "board_todo" | "board_inProgress" | "board_done"; accent: string }[] = [
  { id: "todo", labelKey: "board_todo", accent: "border-t-slate-400" },
  { id: "in_progress", labelKey: "board_inProgress", accent: "border-t-amber-400" },
  { id: "done", labelKey: "board_done", accent: "border-t-teal-400" },
];

function loadBoard(): BoardCard[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as BoardCard[];
  } catch {
    // ignore corrupt storage
  }
  return getDefaultBoard();
}

function Card({ card, onDragStart, onDelete }: { card: BoardCard; onDragStart: (e: DragEvent, id: string) => void; onDelete: (id: string) => void }) {
  return (
    <div
      draggable
      onDragStart={(e) => onDragStart(e, card.id)}
      className="card group cursor-grab overflow-hidden p-3 active:cursor-grabbing"
    >
      <div className={`mb-2 h-1 w-8 rounded-full bg-gradient-to-r ${card.color}`} />
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-ink-900 dark:text-slate-100">{card.title}</p>
          <p className="mt-0.5 text-xs text-ink-600 dark:text-slate-400">{card.phase}</p>
        </div>
        <button
          onClick={() => onDelete(card.id)}
          className="invisible text-xs text-ink-500 hover:text-red-600 group-hover:visible dark:text-slate-500 dark:hover:text-red-400"
          aria-label="Remove card"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

function AddCardForm({ onAdd }: { onAdd: (title: string, phase: string) => void }) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [phase, setPhase] = useState(ALL_PHASES[0]);
  const { t } = useLanguage();

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    onAdd(title.trim(), phase);
    setTitle("");
    setOpen(false);
  }

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="btn-ghost w-full justify-start text-sm">
        + {t("board_addCard")}
      </button>
    );
  }

  return (
    <form onSubmit={submit} className="card flex flex-col gap-2 p-3">
      <input
        autoFocus
        className="input text-sm"
        placeholder="Card title..."
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <select className="input text-sm" value={phase} onChange={(e) => setPhase(e.target.value)}>
        {ALL_PHASES.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <div className="flex gap-2">
        <button type="submit" className="btn-primary flex-1 text-sm">
          {t("board_addCard")}
        </button>
        <button type="button" className="btn-secondary text-sm" onClick={() => setOpen(false)}>
          ✕
        </button>
      </div>
    </form>
  );
}

function BoardContent() {
  const { t } = useLanguage();
  const [cards, setCards] = useState<BoardCard[]>([]);
  const [dragId, setDragId] = useState<string | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<BoardColumnId | null>(null);

  useEffect(() => {
    setCards(loadBoard());
  }, []);

  function persist(next: BoardCard[]) {
    setCards(next);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      // ignore
    }
  }

  function onDrop(column: BoardColumnId) {
    if (!dragId) return;
    persist(cards.map((c) => (c.id === dragId ? { ...c, column } : c)));
    setDragId(null);
    setDragOverColumn(null);
  }

  function addCard(title: string, phase: string) {
    const card: BoardCard = {
      id: `custom-${Date.now()}`,
      phase,
      title,
      column: "todo",
      color: colorForPhase(phase),
    };
    persist([...cards, card]);
  }

  function deleteCard(id: string) {
    persist(cards.filter((c) => c.id !== id));
  }

  function resetBoard() {
    if (confirm("Reset the board to the default phase checklist? Custom cards and moves will be lost.")) {
      persist(getDefaultBoard());
    }
  }

  const counts = {
    todo: cards.filter((c) => c.column === "todo").length,
    in_progress: cards.filter((c) => c.column === "in_progress").length,
    done: cards.filter((c) => c.column === "done").length,
  };
  const total = cards.length || 1;
  const donePct = Math.round((counts.done / total) * 100);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900 dark:text-slate-100">{t("board_title")}</h1>
          <p className="mt-1 text-sm text-ink-600 dark:text-slate-400">{t("board_subtitle")}</p>
        </div>
        <button className="btn-secondary" onClick={resetBoard}>
          {t("board_reset")}
        </button>
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium text-ink-900 dark:text-slate-100">Overall progress</span>
          <span className="text-ink-600 dark:text-slate-400">
            {counts.done}/{cards.length} done
          </span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-ink-700">
          <div
            className="h-full rounded-full bg-gradient-to-r from-brand-500 via-accent-500 to-teal-500 transition-all"
            style={{ width: `${donePct}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {COLUMNS.map((col) => (
          <div
            key={col.id}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOverColumn(col.id);
            }}
            onDragLeave={() => setDragOverColumn((c) => (c === col.id ? null : c))}
            onDrop={() => onDrop(col.id)}
            className={`flex flex-col gap-3 rounded-xl border-t-4 ${col.accent} bg-slate-100/60 p-3 transition dark:bg-ink-800/60 ${
              dragOverColumn === col.id ? "ring-2 ring-brand-300 dark:ring-brand-700" : ""
            }`}
          >
            <div className="flex items-center justify-between px-1">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-700 dark:text-slate-300">
                {t(col.labelKey)}
              </h2>
              <span className="badge bg-white text-ink-600 dark:bg-ink-700 dark:text-slate-300">{counts[col.id]}</span>
            </div>

            <div className="flex flex-col gap-2">
              {cards
                .filter((c) => c.column === col.id)
                .map((card) => (
                  <Card
                    key={card.id}
                    card={card}
                    onDelete={deleteCard}
                    onDragStart={(e, id) => {
                      setDragId(id);
                      e.dataTransfer.effectAllowed = "move";
                    }}
                  />
                ))}
            </div>

            {col.id === "todo" && <AddCardForm onAdd={addCard} />}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function BoardPage() {
  return (
    <RequireAuth>
      <BoardContent />
    </RequireAuth>
  );
}
