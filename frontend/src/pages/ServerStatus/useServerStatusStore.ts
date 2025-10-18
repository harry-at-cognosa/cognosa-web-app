import { createResettableStore } from "../../api/createResettableStore";

export type Subprocess = {
  name: string;
  status_text: string;
  is_good: "success" | "warning" | "danger";
};

type ApiSettings = {
  app_version: string;
  db_version: string;
};

export type RunTask = {
  name: string;
  subprocesses: Subprocess[];
};

export type GroupVDBs = {
  gvdbs_id: number;
  group_id: number;
  gvdbs_seqn: number;
  gvdbs_type: string;
  gvdbs_name: string;
  gvdbs_url: string;
  gvdbs_collection: string;
  gvdbs_status: "success" | "warning" | "danger";
  gvdbs_status_text: string;
};

export type GroupLLMs = {
  gllms_id: number;
  group_id: number;
  gllms_seqn: number;
  gllms_type: string;
  gllms_name: string;
  gllms_api_base: string;
  gllms_model: string;
  gllms_status: "success" | "warning" | "danger";
  gllms_status_text: string;
};

export type ServerStatusResponse = {
  api_settings: ApiSettings;
  run_tasks: RunTask[];
  group_vdbs_rows: GroupVDBs[];
  group_llms_rows: GroupLLMs[];
};

type State = {
  api_settings: ApiSettings;
  run_tasks: RunTask[];
  group_vdbs_rows: GroupVDBs[];
  group_llms_rows: GroupLLMs[];
};

type Actions = {
  setData: (data: ServerStatusResponse) => void;
};

export const useServerStatusStore = createResettableStore<State & Actions>(
  (set) => ({
    api_settings: { app_version: "", db_version: "" },
    run_tasks: [],
    group_vdbs_rows: [],
    group_llms_rows: [],
    setData: (data) =>
      set(() => ({
        api_settings: data.api_settings,
        run_tasks: data.run_tasks,
        group_vdbs_rows: data.group_vdbs_rows,
        group_llms_rows: data.group_llms_rows,
      })),
  })
);
