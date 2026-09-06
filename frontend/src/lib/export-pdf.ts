import { jsPDF } from "jspdf";
import type { DashboardData } from "./types";

export function exportDashboardPdf(data: DashboardData, userEmail: string | undefined) {
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const marginX = 48;
  let y = 56;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(20);
  doc.setTextColor(74, 99, 238); // brand-500
  doc.text("ResearchPilot — Analytics Report", marginX, y);

  y += 22;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(100, 116, 139); // slate-500
  doc.text(`Generated ${new Date().toLocaleString()}${userEmail ? `  ·  ${userEmail}` : ""}`, marginX, y);

  y += 30;
  doc.setDrawColor(226, 232, 240);
  doc.line(marginX, y, 548, y);
  y += 30;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.setTextColor(15, 23, 42);
  doc.text("Workspace Summary", marginX, y);
  y += 22;

  const stats: [string, number][] = [
    ["Papers", data.stats.paper_count],
    ["Experiments", data.stats.experiment_count],
    ["AI Insights", data.stats.ai_insight_count],
    ["Conversations", data.stats.conversation_count],
  ];

  const colWidth = 125;
  stats.forEach(([label, value], idx) => {
    const x = marginX + idx * colWidth;
    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.setTextColor(74, 99, 238);
    doc.text(String(value), x, y);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(100, 116, 139);
    doc.text(label, x, y + 14);
  });
  y += 45;

  doc.setDrawColor(226, 232, 240);
  doc.line(marginX, y, 548, y);
  y += 30;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.setTextColor(15, 23, 42);
  doc.text("Recent Papers", marginX, y);
  y += 20;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  if (data.recent_papers.length === 0) {
    doc.setTextColor(100, 116, 139);
    doc.text("No papers uploaded yet.", marginX, y);
    y += 18;
  } else {
    data.recent_papers.forEach((p) => {
      doc.setTextColor(15, 23, 42);
      const title = p.title || p.filename;
      doc.text(`• ${title}`, marginX, y);
      doc.setTextColor(100, 116, 139);
      doc.text(`[${p.status}]`, 470, y);
      y += 16;
    });
  }

  y += 20;
  doc.setDrawColor(226, 232, 240);
  doc.line(marginX, y, 548, y);
  y += 30;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.setTextColor(15, 23, 42);
  doc.text("Recent Experiments", marginX, y);
  y += 20;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  if (data.recent_experiments.length === 0) {
    doc.setTextColor(100, 116, 139);
    doc.text("No experiments logged yet.", marginX, y);
  } else {
    data.recent_experiments.forEach((e) => {
      doc.setTextColor(15, 23, 42);
      doc.text(`• ${e.name}`, marginX, y);
      doc.setTextColor(100, 116, 139);
      doc.text(e.model || "—", 470, y);
      y += 16;
    });
  }

  doc.save(`researchpilot-report-${new Date().toISOString().slice(0, 10)}.pdf`);
}
