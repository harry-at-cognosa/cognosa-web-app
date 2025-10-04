import { create } from "zustand";
import type { DocTasksResponse } from "../../../models/docTasksResponse";
import type { DocTasksQuery } from "../../../models/docTasksQuery";
import type { DocTasksShortItem } from "../../../models/docTasksShortItem";

interface DocTasksCurrentState {
  doc_task_id: number | null;
  gvdbs_id: number | null;
  setGVDBsID: (gvdbs_id: number | null) => void;
  gllms_id: number | null;
  setGLLMsID: (gllms_id: number | null) => void;
  gc_id: number | null;
  setGCID: (gc_id: number | null) => void;
  status: number | null;
  status_text: string;
  short_name: string | null;
  setShortName: (short_name: string) => void;
  input_text: string | null;
  setInputText: (input_text: string) => void;
  optional_text: string | null;
  setOptionalText: (optional_text: string) => void;
  output_text: string | null;
  is_processing: boolean | null;
  is_error: boolean | null;
  status_pct: number | null;
  setBeforeServerResponse: (query: DocTasksQuery) => void;
  setFromServerResponse: (response: DocTasksResponse) => void;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
  setFromHistory: (item: DocTasksShortItem) => void;
  setNewQuery: () => void;
}

const defaultState = {
  doc_task_id: null,
  gvdbs_id: null,
  gllms_id: null,
  gc_id: null,
  status: null,
  status_text: "",
  short_name: null,
  input_text: null,
  optional_text: null,
  output_text: null,
  is_processing: null,
  is_error: null,
  status_pct: null,
  needReload: false,
};

export const useDocTasksCurrentStore = create<DocTasksCurrentState>((set) => ({
  ...defaultState,
  setGVDBsID: (gvdbs_id: number | null) => set({ gvdbs_id }),
  setGLLMsID: (gllms_id: number | null) => set({ gllms_id }),
  setGCID: (gc_id: number | null) => set({ gc_id }),
  setShortName: (short_name: string) => set({ short_name }),
  setInputText: (input_text: string) => set({ input_text }),
  setOptionalText: (optional_text: string) => set({ optional_text }),
  setBeforeServerResponse: (query: DocTasksQuery) => set(query),
  setFromServerResponse: (response: DocTasksResponse) => set(response),
  setNeedReload: (needReload: boolean) => set({ needReload }),
  setFromHistory: (item: DocTasksShortItem) =>
    set({
      doc_task_id: item.doc_task_id,
      needReload: true,
    }),
  setNewQuery: () => set(defaultState),
}));
