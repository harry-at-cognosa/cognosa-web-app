import { create } from "zustand";

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
  setData: (data: DocTaskOptionsResponse) => void;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
}

export const useDocTaskOptionsStore = create<DocTaskOptionsState>((set) => ({
  data: { group_contexts: [], group_llms: [], group_vdbs: [] },
  setData: (data) => set({ data }),
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
  create<DocTaskOptionsLastUsedState>((set) => ({
    gc_id: null,
    gllms_id: null,
    gvdbs_id: null,
    setLastUsed: (gc_id: number, gllms_id: number, gvdbs_id: number) =>
      set({ gc_id, gllms_id, gvdbs_id }),
  }));
