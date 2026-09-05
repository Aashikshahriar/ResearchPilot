export type ProcessingStatus = "uploaded" | "processing" | "ready" | "failed";

export interface User {
  id: string;
  email: string;
  full_name: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface PaperListItem {
  id: string;
  filename: string;
  title: string | null;
  status: ProcessingStatus;
  page_count: number | null;
  created_at: string;
}

export interface Section {
  id: string;
  title: string;
  content: string;
  order_index: number;
  page_start: number | null;
  page_end: number | null;
}

export interface PaperDetail extends PaperListItem {
  authors: string[] | null;
  abstract: string | null;
  ai_summary: string | null;
  processing_error: string | null;
  file_size_bytes: number;
  sections: Section[];
}

export type FigureType =
  | "architecture_diagram"
  | "flowchart"
  | "graph_plot"
  | "table"
  | "microscopy_image"
  | "mathematical_figure"
  | "other";

export interface Figure {
  id: string;
  paper_id: string;
  page_number: number;
  image_path: string;
  caption: string | null;
  classification: FigureType | null;
  confidence: number | null;
  description: string | null;
  vision_model: string | null;
}

export interface Citation {
  section_title: string;
  chunk_id: string;
  excerpt: string;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  citations: Citation[];
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ComparisonResult {
  research_problem: string;
  methodology: string;
  datasets: string;
  models: string;
  results: string;
  strengths: string;
  limitations: string;
  key_differences: string;
}

export interface Experiment {
  id: string;
  name: string;
  model: string | null;
  dataset: string | null;
  learning_rate: number | null;
  batch_size: number | null;
  epochs: number | null;
  notes: string | null;
  created_at: string;
}

export interface Metric {
  id: string;
  name: string;
  value: number;
  step: number | null;
  created_at: string;
}

export interface DashboardStats {
  paper_count: number;
  experiment_count: number;
  ai_insight_count: number;
  conversation_count: number;
}

export interface DashboardData {
  stats: DashboardStats;
  recent_papers: PaperListItem[];
  recent_experiments: Experiment[];
}

export interface SearchResultItem {
  type: "paper" | "chunk" | "experiment";
  id: string;
  title: string;
  snippet: string;
  paper_id: string | null;
}
