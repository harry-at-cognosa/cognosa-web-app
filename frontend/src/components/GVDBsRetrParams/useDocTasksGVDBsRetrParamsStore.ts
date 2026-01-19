import { create } from "zustand";
import {
  type GVDBsDefRetrParams,
  allowedSearchTypes,
  type GVDBsRetrParamsLoaded,
  type GVDBsRetrParamsState,
  type GVDBsShortRetrParams,
  type DocTasksGVDBsCfgState,
} from "./types";
import { useDefaultGVDBsRetrParamsStore } from "./useDefaultGVDBsRetrParamsStore";

interface DocTasksGVDBsRetrParamsActions {
  copyFromDefault: () => void;
  setFromDocTaskData: (gvdbs_cfg_json: string) => void;
  getShortName: () => string;
  getGVDBsRetrParamsDict: () => DocTasksGVDBsCfgState | null;
}

export const useDocTasksGVDBsRetrParamsStore = create<
  GVDBsRetrParamsLoaded & GVDBsRetrParamsState & DocTasksGVDBsRetrParamsActions
>((set, get) => ({
  search_type: null,
  search_kwargs__similarity: null,
  search_kwargs__mmr: null,
  search_kwargs__similarity_score_threshold: null,
  isLoaded: false,
  setIsLoaded: (isLoaded: boolean) => set({ isLoaded }),
  getGVDBsRetrParamsDict: () => {
    let search_type = get().search_type;
    let sk_sim = get().search_kwargs__similarity;
    let sk_mmr = get().search_kwargs__mmr;
    let sk_sst = get().search_kwargs__similarity_score_threshold;
    if (!(search_type && sk_sim && sk_mmr && sk_sst)) return null;
    if (search_type === "similarity")
      return { search_type, search_kwargs: { ...sk_sim } };
    if (search_type === "mmr")
      return { search_type, search_kwargs: { ...sk_mmr } };
    return { search_type, search_kwargs: { ...sk_sst } };
  },
  getShortName: () => {
    let search_type = get().search_type;
    let sk_sim = get().search_kwargs__similarity;
    let sk_mmr = get().search_kwargs__mmr;
    let sk_sst = get().search_kwargs__similarity_score_threshold;
    if (!(get().isLoaded && search_type && sk_sim && sk_mmr && sk_sst)) {
      return "N/A";
    }
    let text = "";
    if (search_type === "similarity") {
      text = `SIM: ${sk_sim.k}`;
    } else if (search_type === "mmr") {
      text = `MMR: ${sk_mmr.k}/${sk_mmr.fetch_k}/${sk_mmr.lambda_mult}`;
    } else if (search_type === "similarity_score_threshold") {
      text = `SST: ${sk_sst.k}/${sk_sst.score_threshold}`;
    }
    return text;
  },
  setData: (gvdbs_def_retr_params: GVDBsDefRetrParams | string) => {
    try {
      const drp_obj =
        typeof gvdbs_def_retr_params === "string"
          ? JSON.parse(gvdbs_def_retr_params)
          : gvdbs_def_retr_params;
      if (!allowedSearchTypes.includes(drp_obj.search_type))
        throw "Wrong search type";
      set({ ...drp_obj, isLoaded: true });
    } catch (e) {
      console.log(e);
    }
  },
  copyFromDefault: () => {
    const defaultState = useDefaultGVDBsRetrParamsStore.getState();
    if (
      !(
        defaultState.isLoaded &&
        defaultState.search_kwargs__similarity &&
        defaultState.search_kwargs__mmr &&
        defaultState.search_kwargs__similarity_score_threshold
      )
    ) {
      console.warn("Default store is not loaded yet");
      return;
    }

    set({
      search_type: defaultState.search_type,
      search_kwargs__similarity: { ...defaultState.search_kwargs__similarity },
      search_kwargs__mmr: { ...defaultState.search_kwargs__mmr },
      search_kwargs__similarity_score_threshold: {
        ...defaultState.search_kwargs__similarity_score_threshold,
      },
      isLoaded: true,
    });
  },
  setFromDocTaskData: (gvdbs_cfg_json: string) => {
    let cur_sk_sim = get().search_kwargs__similarity;
    let cur_sk_mmr = get().search_kwargs__mmr;
    let cur_sk_sst = get().search_kwargs__similarity_score_threshold;

    if (!(get().isLoaded && cur_sk_sim && cur_sk_mmr && cur_sk_sst)) {
      console.warn("DocTask store is not loaded yet");
      return;
    }
    try {
      const gvdbs_cfg_obj: GVDBsShortRetrParams = JSON.parse(gvdbs_cfg_json);
      const search_type = gvdbs_cfg_obj.search_type;
      if (!allowedSearchTypes.includes(search_type)) throw "Wrong search type";
      set({ search_type });
      const search_kwargs = gvdbs_cfg_obj.search_kwargs;
      if (!search_kwargs) {
        console.warn("No search_kwargs found");
        return;
      }
      const { k, fetch_k, lambda_mult, score_threshold } =
        gvdbs_cfg_obj.search_kwargs;
      if (search_type === "similarity") {
        if (k !== undefined) cur_sk_sim = { ...cur_sk_sim, k };
        set({ search_kwargs__similarity: cur_sk_sim });
      }
      if (search_type === "mmr") {
        if (k !== undefined) cur_sk_mmr = { ...cur_sk_mmr, k };
        if (fetch_k !== undefined) cur_sk_mmr = { ...cur_sk_mmr, fetch_k };
        if (lambda_mult !== undefined)
          cur_sk_mmr = { ...cur_sk_mmr, lambda_mult };
        set({ search_kwargs__mmr: cur_sk_mmr });
      }
      if (search_type === "similarity_score_threshold") {
        if (k !== undefined) cur_sk_sst = { ...cur_sk_sst, k };
        if (score_threshold !== undefined)
          cur_sk_sst = { ...cur_sk_sst, score_threshold };
        set({ search_kwargs__similarity_score_threshold: cur_sk_sst });
      }
    } catch (e) {
      console.log(e);
    }
  },
}));
