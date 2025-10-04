export type DocTasksResponse = {
  doc_task_id: number;
  gvdbs_id: number;
  gc_id: number;
  status: number;
  status_text: string;
  short_name: string;
  input_text: string;
  optional_text: string;
  output_text: string;
  is_processing: boolean;
  is_error: boolean;
  status_pct: number;
};
