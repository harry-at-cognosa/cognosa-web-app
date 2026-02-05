import type { DocTasksResponse } from "../models/docTasksResponse";
import type { DocTasksQuery } from "../models/docTasksQuery";
import type { DocTasksShortItem } from "../models/docTasksShortItem";
import { createResettableStore } from "../../../api/createResettableStore";
import type { DocTasksGVDBsCfgState } from "../../../components/GVDBsRetrParams/types";

interface DocTasksCurrentState {
  doc_task_id: number | null;
  gvdbs_id: number | null;
  setGVDBsID: (gvdbs_id: number | null) => void;
  gvdbs_cfg_json: DocTasksGVDBsCfgState | null;
  gllms_id: number | null;
  setGLLMsID: (gllms_id: number | null) => void;
  gc_id: number | null;
  setGCID: (gc_id: number | null) => void;
  context_json: string | null;
  status: number | null;
  status_text: string;
  short_name: string | null;
  setShortName: (short_name: string) => void;
  input_text: string | null;
  setInputText: (input_text: string) => void;
  optional_text: string | null;
  setOptionalText: (optional_text: string) => void;
  output_text: string | null;
  question_number: number;
  output_text_2: string | null;
  vdb_query_seconds: number | null;
  llm_query_seconds: number | null;
  llm_tokens_sent: number | null;
  llm_tokens_received: number | null;
  is_processing: boolean | null;
  is_error: boolean | null;
  status_pct: number | null;
  setBeforeServerResponse: (query: DocTasksQuery) => void;
  setFromServerResponse: (response: DocTasksResponse) => void;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
  needReloadFromHistory: boolean;
  setFromHistory: (item: DocTasksShortItem) => void;
  setNewQuery: () => void;
  previousQuery: DocTasksQuery | null;
  isSameAsPreviousQuery: (query: DocTasksQuery) => boolean;
  cloneQuery: () => void;
}

const defaultState = {
  doc_task_id: null,
  gvdbs_id: null,
  gvdbs_cfg_json: null,
  gllms_id: null,
  gc_id: null,
  context_json: null,
  status: null,
  status_text: "",
  short_name: null,
  input_text: null,
  optional_text: null,
  output_text: null,
  question_number: 0,
  output_text_2: null,
  vdb_query_seconds: null,
  llm_query_seconds: null,
  llm_tokens_sent: null,
  llm_tokens_received: null,
  is_processing: null,
  is_error: null,
  status_pct: null,
  needReload: false,
  needReloadFromHistory: false,
  previousQuery: null,
};

function responseToQuery(response: DocTasksResponse): DocTasksQuery {
  return {
    doc_task_id: response.doc_task_id,
    gvdbs_id: response.gvdbs_id,
    gvdbs_cfg_json: JSON.parse(response.gvdbs_cfg_json),
    gllms_id: response.gllms_id,
    gc_id: response.gc_id,
    short_name: response.short_name,
    input_text: response.input_text,
    optional_text: response.optional_text,
  };
}

function compareWithPreviousQuery(
  query1: DocTasksQuery,
  query2: DocTasksQuery | null,
): boolean {
  function trimStr(str: string) {
    // convert multiple whitespaces to single space + trim
    return str.replace(/\s+/g, " ").trim();
  }
  if (!(query1 && query2)) return false;
  if (query1.doc_task_id !== query2.doc_task_id) return false;
  if (query1.gvdbs_id !== query2.gvdbs_id) return false;
  if (query1.gllms_id !== query2.gllms_id) return false;
  if (query1.gc_id !== query2.gc_id) return false;
  if (trimStr(query1.input_text) !== trimStr(query2.input_text)) return false;
  if (trimStr(query1.optional_text) !== trimStr(query2.optional_text))
    return false;
  const cfg1 = query1.gvdbs_cfg_json;
  const cfg2 = query2.gvdbs_cfg_json;
  if (!(cfg1 && cfg2)) return false;
  // Compare Retrieval Parameters
  const sk1 = cfg1.search_kwargs;
  const sk2 = cfg2.search_kwargs;
  if (!(sk1 && sk2)) return false;
  if (cfg1.search_type !== cfg2.search_type) return false;
  if (Number(sk1.k) !== Number(sk2.k)) return false;
  if (cfg1.search_type === "mmr") {
    if (Number(sk1.fetch_k) !== Number(sk2.fetch_k)) return false;
    if (Number(sk1.lambda_mult) !== Number(sk2.lambda_mult)) return false;
  }
  if (cfg1.search_type === "similarity_score_threshold") {
    if (Number(sk1.score_threshold) !== Number(sk2.score_threshold))
      return false;
  }
  // Compare Retrieval Filters
  if (JSON.stringify(cfg1.filters) !== JSON.stringify(cfg2.filters))
    return false;
  return true;
}

export const useDocTasksCurrentStore =
  createResettableStore<DocTasksCurrentState>((set, get) => ({
    ...defaultState,
    setGVDBsID: (gvdbs_id: number | null) => set({ gvdbs_id }),
    setGLLMsID: (gllms_id: number | null) => set({ gllms_id }),
    setGCID: (gc_id: number | null) => set({ gc_id }),
    setShortName: (short_name: string) => set({ short_name }),
    setInputText: (input_text: string) => set({ input_text }),
    setOptionalText: (optional_text: string) => set({ optional_text }),
    setBeforeServerResponse: (query: DocTasksQuery) => {
      set({ ...query, previousQuery: query });
    },
    setFromServerResponse: (response: DocTasksResponse) => {
      const previousQuery = get().previousQuery || responseToQuery(response);
      set({
        ...response,
        gvdbs_cfg_json: JSON.parse(response.gvdbs_cfg_json),
        previousQuery,
        needReloadFromHistory: false,
      });
    },
    setNeedReload: (needReload: boolean) => set({ needReload }),
    setFromHistory: (item: DocTasksShortItem) =>
      set({
        doc_task_id: item.doc_task_id,
        status: null,
        status_text: "",
        question_number: 0,
        context_json: null,
        previousQuery: null,
        needReload: true,
        needReloadFromHistory: true,
        output_text: null,
        output_text_2: null,
        vdb_query_seconds: null,
        llm_query_seconds: null,
        llm_tokens_sent: null,
        llm_tokens_received: null,
        is_error: null,
      }),
    setNewQuery: () => set(defaultState),
    isSameAsPreviousQuery: (query: DocTasksQuery) => {
      return compareWithPreviousQuery(query, get().previousQuery);
    },
    cloneQuery: () =>
      set({
        doc_task_id: null,
        status: null,
        status_text: "",
        question_number: 0,
        context_json: null,
        output_text: null,
        output_text_2: null,
        vdb_query_seconds: null,
        llm_query_seconds: null,
        llm_tokens_sent: null,
        llm_tokens_received: null,
        is_processing: null,
        is_error: null,
      }),
  }));
