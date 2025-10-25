export type DocTasksResponse = {
  doc_task_id: number;
  gvdbs_id: number;
  gllms_id: number;
  gc_id: number;
  status: number;
  status_text: string;
  short_name: string;
  input_text: string;
  optional_text: string;
  output_text: string;
  vdb_query_seconds: number | null;
  llm_query_seconds: number | null;
  llm_tokens_sent: number | null;
  llm_tokens_received: number | null;
  is_processing: boolean;
  is_error: boolean;
  status_pct: number;
};
