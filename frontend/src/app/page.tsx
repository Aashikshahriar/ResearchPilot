import Link from "next/link";

const FEATURES = [
  {
    title: "Grounded RAG chat",
    description: "Ask questions about any uploaded paper and get answers retrieved and cited from the actual text — not hallucinated.",
  },
  {
    title: "Figure understanding",
    description: "Every extracted figure is classified (architecture diagram, plot, table, and more) and described automatically.",
  },
  {
    title: "Structured comparison",
    description: "Compare two or more papers side by side across methodology, datasets, results, and limitations.",
  },
  {
    title: "Experiment tracking",
    description: "Log models, hyperparameters, and metrics for your own experiments, and visualize progress over time.",
  },
  {
    title: "Full-text research search",
    description: "Search across every paper, chunk, and experiment in your personal workspace in one place.",
  },
  {
    title: "Built for real pipelines",
    description: "Async background processing, pgvector-backed retrieval, and swappable LLM/vision providers under the hood.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2 text-lg font-semibold text-ink-900">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500 text-white">R</span>
          ResearchPilot
        </div>
        <nav className="flex items-center gap-3">
          <Link href="/login" className="btn-secondary">
            Log in
          </Link>
          <Link href="/register" className="btn-primary">
            Get started
          </Link>
        </nav>
      </header>

      <section className="mx-auto max-w-4xl px-6 pb-20 pt-16 text-center">
        <span className="badge mb-6 bg-brand-50 text-brand-700">AI-powered research workspace</span>
        <h1 className="text-4xl font-bold tracking-tight text-ink-900 sm:text-5xl">
          Read, chat with, and compare papers — grounded in what they actually say.
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-ink-600">
          Upload academic PDFs and let ResearchPilot extract sections, index them for retrieval, classify their
          figures with computer vision, and answer your questions with citations back to the source.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link href="/register" className="btn-primary px-6 py-3 text-base">
            Create your workspace
          </Link>
          <Link href="/login" className="btn-secondary px-6 py-3 text-base">
            I already have an account
          </Link>
        </div>
      </section>

      <section className="border-t border-slate-100 bg-slate-50 py-16">
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="card p-6">
              <h3 className="font-semibold text-ink-900">{f.title}</h3>
              <p className="mt-2 text-sm text-ink-600">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-slate-100 py-8 text-center text-sm text-ink-600">
        ResearchPilot &mdash; a portfolio project demonstrating full-stack AI application engineering.
      </footer>
    </div>
  );
}
