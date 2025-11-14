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
interface ActionsFromData {
  setDefaultValues: () => void;
  setFromData: (gvdbs_cfg_json: string) => void;
}

interface ModalGVDBsCfgState {
  search_type_name: [SearchType, string][];
  search_type: SearchType;
  search_kwargs: SearchKwargsType;
}

const defaultGVDBsCfgState: DocTasksGVDBsCfgState = {
  search_type: "similarity",
  search_kwargs: {
    k: 10,
    fetch_k: 20,
    lambda_mult: 0.5,
    score_threshold: 0.5,
  },
};

export const useModalGVDBsCfgStore = create<ModalGVDBsCfgState & Actions>(
  (set) => ({
    search_type: defaultGVDBsCfgState.search_type,
    search_kwargs: { ...defaultGVDBsCfgState.search_kwargs },
    search_type_name: [
      ["similarity", "Similarity"],
      ["mmr", "MMR"],
      ["similarity_score_threshold", "Similarity Score Threshold"],
    ],
    setSearchType: (type) => set({ search_type: type }),
    setSearchKwargs: (kwargs) => set({ search_kwargs: kwargs }),
    setKwargsField: (field, value) =>
      set((state) => ({
        search_kwargs: { ...state.search_kwargs, [field]: value },
      })),
  })
);

export const useDocTasksGVDBsCfgStore = create<
  DocTasksGVDBsCfgState & Actions & ActionsFromData
>((set) => ({
  search_type: defaultGVDBsCfgState.search_type,
  search_kwargs: { ...defaultGVDBsCfgState.search_kwargs },
  setSearchType: (type) => set({ search_type: type }),
  setSearchKwargs: (kwargs) => set({ search_kwargs: kwargs }),
  setKwargsField: (field, value) =>
    set((state) => ({
      search_kwargs: { ...state.search_kwargs, [field]: value },
    })),
  setDefaultValues: () => {
    set({
      search_type: defaultGVDBsCfgState.search_type,
      search_kwargs: { ...defaultGVDBsCfgState.search_kwargs },
    });
  },
  setFromData: (gvdbs_cfg_json: string) => {
    let search_type: SearchType = defaultGVDBsCfgState.search_type;
    let search_kwargs: SearchKwargsType = {
      ...defaultGVDBsCfgState.search_kwargs,
    };
    try {
      const gvdbs_cfg_obj: DocTasksGVDBsCfgState = JSON.parse(gvdbs_cfg_json);
      if (!gvdbs_cfg_obj.search_type) throw "Wrong search type";
      search_type = gvdbs_cfg_obj.search_type;
      search_kwargs = { ...gvdbs_cfg_obj.search_kwargs };
    } catch {
      search_type = defaultGVDBsCfgState.search_type;
      search_kwargs = { ...defaultGVDBsCfgState.search_kwargs };
    } finally {
      set({ search_type: search_type, search_kwargs: { ...search_kwargs } });
    }
  },
}));
