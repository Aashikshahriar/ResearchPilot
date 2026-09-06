import { ReactNode } from "react";

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="card flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
      <h3 className="text-base font-semibold text-ink-900 dark:text-slate-100">{title}</h3>
      {description && <p className="max-w-sm text-sm text-ink-600 dark:text-slate-400">{description}</p>}
      {action}
    </div>
  );
}
