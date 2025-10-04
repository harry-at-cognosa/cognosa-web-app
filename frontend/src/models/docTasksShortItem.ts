export type DocTasksShortItem = {
  doc_task_id: number;
  status: number;
  status_text: string;
  short_name: string;
  created_at: string;
  is_processing: boolean;
  is_error: boolean;
  status_pct: number;
};
