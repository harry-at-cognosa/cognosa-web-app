import { create } from "zustand";
import {
  type GVDBsDefRetrParams,
  type SearchType,
  type SearchKwargsSIM,
  type SearchKwargsMMR,
  type SearchKwargsSST,
  allowedSearchTypes,
  type GVDBsRetrParamsState,
  type GVDBsRetrParamsLoaded,
} from "./types";

interface ActionsModal {
  getJSON: () => string;
  setSearchType: (type: SearchType) => void;
  setKwargsFieldSIM: (field: keyof SearchKwargsSIM, value: number) => void;
  setKwargsFieldMMR: (field: keyof SearchKwargsMMR, value: number) => void;
  setKwargsFieldSST: (field: keyof SearchKwargsSST, value: number) => void;
}

export const useModalGVDBsRetrParamsStore = create<
  GVDBsRetrParamsLoaded & GVDBsRetrParamsState & ActionsModal
>((set, get) => ({
  search_type: null,
  search_kwargs__similarity: null,
  search_kwargs__mmr: null,
  search_kwargs__similarity_score_threshold: null,
  getJSON: () => {
    return JSON.stringify({
      search_type: get().search_type,
      search_kwargs__similarity: get().search_kwargs__similarity,
      search_kwargs__mmr: get().search_kwargs__mmr,
      search_kwargs__similarity_score_threshold:
        get().search_kwargs__similarity_score_threshold,
    });
  },
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
  setSearchType: (search_type: SearchType) => set({ search_type }),
  setKwargsFieldSIM: (field: keyof SearchKwargsSIM, value: number) =>
    set((state) => ({
      search_kwargs__similarity: {
        ...state.search_kwargs__similarity,
        [field]: value,
      } as SearchKwargsSIM,
    })),
  setKwargsFieldMMR: (field: keyof SearchKwargsMMR, value: number) =>
    set((state) => ({
      search_kwargs__mmr: {
        ...state.search_kwargs__mmr,
        [field]: value,
      } as SearchKwargsMMR,
    })),
  setKwargsFieldSST: (field: keyof SearchKwargsSST, value: number) =>
    set((state) => ({
      search_kwargs__similarity_score_threshold: {
        ...state.search_kwargs__similarity_score_threshold,
        [field]: value,
      } as SearchKwargsSST,
    })),
}));
