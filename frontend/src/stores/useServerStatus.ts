import { create } from "zustand";

export type Subprocess = {
  name: string;
  status_text: string;
  is_good: "success" | "warning" | "danger";
};

export type RunTask = {
  name: string;
  subprocesses: Subprocess[];
};

export type GroupVDBS = {
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

export type ServerStatusResponse = {
  run_tasks: RunTask[];
  group_vdbs_rows: GroupVDBS[];
};

type State = {
  run_tasks: RunTask[];
  group_vdbs_rows: GroupVDBS[];
};

type Actions = {
  setData: (data: ServerStatusResponse) => void;
  clear: () => void;
};

export const useServerStatusStore = create<State & Actions>((set) => ({
  run_tasks: [],
  group_vdbs_rows: [],
  setData: (data) =>
    set(() => ({
      run_tasks: data.run_tasks,
      group_vdbs_rows: data.group_vdbs_rows,
    })),
  clear: () => set(() => ({ run_tasks: [], group_vdbs_rows: [] })),
}));
