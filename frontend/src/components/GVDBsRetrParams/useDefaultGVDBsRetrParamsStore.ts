import { create } from "zustand";
import {
  type GVDBsDefRetrParams,
  allowedSearchTypes,
  type GVDBsRetrParamsLoaded,
  type GVDBsRetrParamsState,
} from "./types";

export const useDefaultGVDBsRetrParamsStore = create<
  GVDBsRetrParamsLoaded & GVDBsRetrParamsState
>((set) => ({
  search_type: null,
  search_kwargs__similarity: null,
  search_kwargs__mmr: null,
  search_kwargs__similarity_score_threshold: null,
  isLoaded: false,
  setIsLoaded: (isLoaded: boolean) => set({ isLoaded }),
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
}));
