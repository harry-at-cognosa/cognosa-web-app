import axiosClient from "../../../api/axiosClient";
import { createResettableStore } from "../../../api/createResettableStore";

export type GroupContexts = {
  gc_id: number;
  group_id: number;
  gc_seqn: number;
  gc_name: string;
  gc_text: string;
};

export type GroupLLMs = {
  gllms_id: number;
  group_id: number;
  gllms_name: string;
  gllms_status: "success" | "warning" | "danger";
};

export type GroupVDBs = {
  gvdbs_id: number;
  group_id: number;
  gvdbs_name: string;
  gvdbs_status: "success" | "warning" | "danger";
};

export interface DocTaskOptionsResponse {
  group_contexts: GroupContexts[];
  group_llms: GroupLLMs[];
  group_vdbs: GroupVDBs[];
}

interface DocTaskOptionsState {
  data: DocTaskOptionsResponse;
  fetchData: () => Promise<void>;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
}

export const useDocTaskOptionsStore =
  createResettableStore<DocTaskOptionsState>((set) => ({
    data: {
      group_contexts: [],
      group_llms: [],
      group_vdbs: [],
    },
    fetchData: async () => {
      try {
        const response = await axiosClient.get<DocTaskOptionsResponse>(
          "/doc_tasks/options"
        );
        const data = response.data;
        // use success rows first
        data.group_vdbs.sort((a, b) => {
          return (
            Number(b.gvdbs_status === "success") -
            Number(a.gvdbs_status === "success")
          );
        });
        data.group_llms.sort((a, b) => {
          return (
            Number(b.gllms_status === "success") -
            Number(a.gllms_status === "success")
          );
        });
        set({ data, needReload: false });
      } catch {
        alert("Error during fetching /doc_tasks/options");
      } finally {
      }
    },
    needReload: true,
    setNeedReload: (needReload: boolean) => set({ needReload }),
  }));

interface DocTaskOptionsLastUsedState {
  gc_id: number | null;
  gllms_id: number | null;
  gvdbs_id: number | null;
  setLastUsed: (gc_id: number, gllms_id: number, gvdbs_id: number) => void;
}

export const useDocTaskOptionsLastUsedStore =
  createResettableStore<DocTaskOptionsLastUsedState>((set) => ({
    gc_id: null,
    gllms_id: null,
    gvdbs_id: null,
    setLastUsed: (gc_id: number, gllms_id: number, gvdbs_id: number) =>
      set({ gc_id, gllms_id, gvdbs_id }),
  }));
