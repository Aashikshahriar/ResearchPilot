import clsx from "clsx";
import type { ProcessingStatus } from "@/lib/types";

const STYLES: Record<ProcessingStatus, string> = {
  uploaded: "bg-slate-100 text-slate-700",
  processing: "bg-amber-100 text-amber-700",
  ready: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
};

export function StatusBadge({ status }: { status: ProcessingStatus }) {
  return <span className={clsx("badge", STYLES[status])}>{status}</span>;
}
