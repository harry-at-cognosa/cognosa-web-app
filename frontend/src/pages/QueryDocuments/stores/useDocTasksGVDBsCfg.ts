import { create } from "zustand";

export type SearchKwargsType = {
  k: number;
  fetch_k: number;
  lambda_mult: number;
  score_threshold: number;
};

export type SearchType = "similarity" | "mmr" | "similarity_score_threshold";

export interface DocTasksGVDBsCfgState {
  search_type: SearchType;
  search_kwargs: SearchKwargsType;
}

interface Actions {
  setSearchType: (type: SearchType) => void;
  setSearchKwargs: (kwargs: SearchKwargsType) => void;
  setKwargsField: (
    field: keyof SearchKwargsType,
    value: number | undefined
  ) => void;
}

interface ModalGVDBsCfgState {
  search_type: SearchType;
  search_kwargs: SearchKwargsType;
}
export const useModalGVDBsCfgStore = create<ModalGVDBsCfgState & Actions>(
  (set) => ({
    search_type: "similarity",
    search_kwargs: {
      k: 10,
      fetch_k: 20,
      lambda_mult: 0.5,
      score_threshold: 0.5,
    },
    setSearchType: (type) => set({ search_type: type }),
    setSearchKwargs: (kwargs) => set({ search_kwargs: kwargs }),
    setKwargsField: (field, value) =>
      set((state) => ({
        search_kwargs: { ...state.search_kwargs, [field]: value },
      })),
  })
);

export const useDocTasksGVDBsCfgStore = create<DocTasksGVDBsCfgState & Actions>(
  (set) => ({
    search_type: "similarity",
    search_kwargs: {
      k: 10,
      fetch_k: 20,
      lambda_mult: 0.5,
      score_threshold: 0.5,
    },
    setSearchType: (type) => set({ search_type: type }),
    setSearchKwargs: (kwargs) => set({ search_kwargs: kwargs }),
    setKwargsField: (field, value) =>
      set((state) => ({
        search_kwargs: { ...state.search_kwargs, [field]: value },
      })),
  })
);
