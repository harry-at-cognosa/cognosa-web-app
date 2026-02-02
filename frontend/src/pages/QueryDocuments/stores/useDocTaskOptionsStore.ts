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
  gllms_seqn: number;
  gllms_name: string;
  gllms_status: "success" | "warning" | "danger";
};

export type GroupVDBs = {
  gvdbs_id: number;
  group_id: number;
  gvdbs_seqn: number;
  gvdbs_name: string;
  gvdbs_retr_params: string | null;
  gvdbs_retr_filters: string | null;
  gvdbs_status: "success" | "warning" | "danger";
};

export interface DocTaskOptionsResponse {
  group_contexts: GroupContexts[];
  group_llms: GroupLLMs[];
  group_vdbs: GroupVDBs[];
}

interface DocTaskOptionsState {
  data: DocTaskOptionsResponse;
  gvdbs_id__row: Record<number, GroupVDBs>;
  gllms_id__row: Record<number, GroupLLMs>;
  fetchData: () => Promise<void>;
  initiallyLoaded: boolean;
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
    gvdbs_id__row: {},
    gllms_id__row: {},
    initiallyLoaded: false,
    fetchData: async () => {
      try {
        const response =
          await axiosClient.get<DocTaskOptionsResponse>("/doc_tasks/options");
        const data = response.data;
        // sort group_vdbs by (is success?, gvdbs_seqn)
        data.group_vdbs.sort((a, b) => {
          const aIsSuccess = a.gvdbs_status === "success" ? 1 : 0;
          const bIsSuccess = b.gvdbs_status === "success" ? 1 : 0;
          if (bIsSuccess !== aIsSuccess) {
            return bIsSuccess - aIsSuccess; // success first
          }
          return a.gvdbs_seqn - b.gvdbs_seqn; // If same status, sort by seqn ascending
        });
        data.group_vdbs.push({
          gvdbs_id: -1,
          group_id: -1,
          gvdbs_seqn: 1000,
          gvdbs_name: "No Document search, use only LLM",
          gvdbs_retr_params: null,
          gvdbs_retr_filters: null,
          gvdbs_status: "success",
        });
        const gvdbs_id__row = data.group_vdbs.reduce(
          (acc: Record<number, GroupVDBs>, obj) => {
            acc[obj.gvdbs_id] = obj;
            return acc;
          },
          {},
        );
        // sort group_llms by (is success?, gllms_seqn)
        data.group_llms.sort((a, b) => {
          const aIsSuccess = a.gllms_status === "success" ? 1 : 0;
          const bIsSuccess = b.gllms_status === "success" ? 1 : 0;
          if (bIsSuccess !== aIsSuccess) {
            return bIsSuccess - aIsSuccess; // success first
          }
          return a.gllms_seqn - b.gllms_seqn; // If same status, sort by seqn ascending
        });
        const gllms_id__row = data.group_llms.reduce(
          (acc: Record<number, GroupLLMs>, obj) => {
            acc[obj.gllms_id] = obj;
            return acc;
          },
          {},
        );
        set({
          data,
          gvdbs_id__row,
          gllms_id__row,
          needReload: false,
          initiallyLoaded: true,
        });
      } catch {
        alert("Error during fetching /doc_tasks/options");
      } finally {
      }
    },
    needReload: true,
    setNeedReload: (needReload: boolean) => set({ needReload }),
  }));
