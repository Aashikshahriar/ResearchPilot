import clsx from "clsx";
import type { ProcessingStatus } from "@/lib/types";

const STYLES: Record<ProcessingStatus, string> = {
  uploaded: "bg-slate-100 text-slate-700 dark:bg-ink-700 dark:text-slate-300",
  processing: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  ready: "bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

export function StatusBadge({ status }: { status: ProcessingStatus }) {
  return <span className={clsx("badge", STYLES[status])}>{status}</span>;
}
