import type { DocTasksGVDBsCfgState } from "../stores/useDocTasksGVDBsCfg";

export type DocTasksQuery = {
  gvdbs_id: number;
  gvdbs_cfg_json?: DocTasksGVDBsCfgState;
  gllms_id: number;
  gc_id: number;
  short_name: string;
  input_text: string;
  optional_text: string;
};
