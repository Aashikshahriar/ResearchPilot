export type BoardColumnId = "todo" | "in_progress" | "done";

export interface BoardCard {
  id: string;
  phase: string;
  title: string;
  column: BoardColumnId;
  color: string; // tailwind gradient classes for the card's accent bar
}

const PHASE_COLORS: Record<string, string> = {
  "Phase 2 — Paper Management": "from-brand-500 to-brand-400",
  "Phase 3 — Document Intelligence": "from-teal-500 to-teal-400",
  "Phase 4 — RAG": "from-accent-500 to-accent-400",
  "Phase 5 — Vision": "from-amber-500 to-amber-400",
  "Phase 6 — Research Features": "from-rose-500 to-rose-400",
  "Phase 7 — Production Quality": "from-brand-500 via-accent-500 to-teal-500",
};

interface SeedItem {
  phase: string;
  title: string;
  column: BoardColumnId;
}

// Reflects the actual, verified state of the codebase at the time this board
// was added -- not aspirational. Update columns here as work genuinely lands.
const SEED: SeedItem[] = [
  // Phase 2 — Paper Management
  { phase: "Phase 2 — Paper Management", title: "Upload", column: "done" },
  { phase: "Phase 2 — Paper Management", title: "Storage", column: "done" },
  { phase: "Phase 2 — Paper Management", title: "Metadata", column: "done" },
  { phase: "Phase 2 — Paper Management", title: "Paper list", column: "done" },
  { phase: "Phase 2 — Paper Management", title: "Paper detail", column: "done" },
  { phase: "Phase 2 — Paper Management", title: "Processing states", column: "done" },

  // Phase 3 — Document Intelligence
  { phase: "Phase 3 — Document Intelligence", title: "PDF extraction", column: "done" },
  { phase: "Phase 3 — Document Intelligence", title: "Section detection", column: "done" },
  { phase: "Phase 3 — Document Intelligence", title: "Chunking", column: "done" },
  { phase: "Phase 3 — Document Intelligence", title: "Embeddings", column: "done" },
  { phase: "Phase 3 — Document Intelligence", title: "pgvector", column: "done" },

  // Phase 4 — RAG
  { phase: "Phase 4 — RAG", title: "Retrieval", column: "done" },
  { phase: "Phase 4 — RAG", title: "Chat", column: "done" },
  { phase: "Phase 4 — RAG", title: "Conversation storage", column: "done" },
  { phase: "Phase 4 — RAG", title: "Citations/references", column: "done" },
  { phase: "Phase 4 — RAG", title: "Streaming if practical", column: "todo" },

  // Phase 5 — Vision
  { phase: "Phase 5 — Vision", title: "Figure extraction", column: "done" },
  { phase: "Phase 5 — Vision", title: "Figure storage", column: "done" },
  { phase: "Phase 5 — Vision", title: "Classification", column: "done" },
  { phase: "Phase 5 — Vision", title: "Figure descriptions", column: "done" },

  // Phase 6 — Research Features
  { phase: "Phase 6 — Research Features", title: "Summary", column: "done" },
  { phase: "Phase 6 — Research Features", title: "Paper comparison", column: "done" },
  { phase: "Phase 6 — Research Features", title: "Notes", column: "done" },
  { phase: "Phase 6 — Research Features", title: "Experiment tracking", column: "done" },
  { phase: "Phase 6 — Research Features", title: "Analytics", column: "done" },

  // Phase 7 — Production Quality
  { phase: "Phase 7 — Production Quality", title: "Testing", column: "done" },
  { phase: "Phase 7 — Production Quality", title: "Security review", column: "todo" },
  { phase: "Phase 7 — Production Quality", title: "Logging", column: "in_progress" },
  { phase: "Phase 7 — Production Quality", title: "Error handling", column: "done" },
  { phase: "Phase 7 — Production Quality", title: "Performance review", column: "todo" },
  { phase: "Phase 7 — Production Quality", title: "UI polish", column: "in_progress" },
  { phase: "Phase 7 — Production Quality", title: "Documentation", column: "done" },
];

export function getDefaultBoard(): BoardCard[] {
  return SEED.map((item, idx) => ({
    id: `seed-${idx}`,
    phase: item.phase,
    title: item.title,
    column: item.column,
    color: PHASE_COLORS[item.phase] ?? "from-brand-500 to-accent-500",
  }));
}

export function colorForPhase(phase: string): string {
  return PHASE_COLORS[phase] ?? "from-brand-500 to-accent-500";
}

export const ALL_PHASES = Object.keys(PHASE_COLORS);
