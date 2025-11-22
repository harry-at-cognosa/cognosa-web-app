import { createResettableStore } from "../../api/createResettableStore";

type ApiSettings = {
  app_version: string;
  db_version: string;
};

type GroupVDBs = {
  gvdbs_name: string;
  gvdbs_status: "success" | "warning" | "danger";
  gvdbs_status_text: string;
};

type GroupLLMs = {
  gllms_name: string;
  gllms_status: "success" | "warning" | "danger";
  gllms_status_text: string;
};

export type ServerStatusResponse = {
  api_settings: ApiSettings;
  group_vdbs_rows: GroupVDBs[];
  group_llms_rows: GroupLLMs[];
};

type State = {
  api_settings: ApiSettings;
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
    setData: (data) => set(data),
  })
);
