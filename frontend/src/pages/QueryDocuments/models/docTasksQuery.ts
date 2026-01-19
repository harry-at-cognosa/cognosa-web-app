import type { DocTasksGVDBsCfgState } from "../../../components/GVDBsRetrParams/types";

export type DocTasksQuery = {
  doc_task_id: number | null;
  gvdbs_id: number;
  gvdbs_cfg_json: DocTasksGVDBsCfgState;
  gllms_id: number;
  gc_id: number;
  short_name: string;
  input_text: string;
  optional_text: string;
};
