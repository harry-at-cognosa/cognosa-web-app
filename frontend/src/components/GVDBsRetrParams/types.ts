import type { DocTasksGVDBsRetrFiltersRequest } from "../GVDBsRetrFilters/types";

export const allowedSearchTypes = [
  "similarity",
  "mmr",
  "similarity_score_threshold",
];

export type SearchType = "similarity" | "mmr" | "similarity_score_threshold";

export interface SearchKwargs {
  k: number;
  fetch_k?: number;
  lambda_mult?: number;
  score_threshold?: number;
}

export interface DocTasksGVDBsCfgState {
  search_type: SearchType;
  search_kwargs: SearchKwargs;
  filters?: DocTasksGVDBsRetrFiltersRequest;
}

export interface SearchKwargsSIM {
  k: number;
}
export interface SearchKwargsMMR {
  k: number;
  fetch_k: number;
  lambda_mult: number;
}
export interface SearchKwargsSST {
  k: number;
  score_threshold: number;
}

export interface GVDBsShortRetrParams {
  search_type: SearchType;
  search_kwargs: SearchKwargs;
}

export interface GVDBsDefRetrParams {
  search_type: SearchType;
  search_kwargs__similarity: SearchKwargsSIM;
  search_kwargs__mmr: SearchKwargsMMR;
  search_kwargs__similarity_score_threshold: SearchKwargsSST;
}

export interface GVDBsRetrParamsState {
  search_type: SearchType | null;
  search_kwargs__similarity: SearchKwargsSIM | null;
  search_kwargs__mmr: SearchKwargsMMR | null;
  search_kwargs__similarity_score_threshold: SearchKwargsSST | null;
  setData: (gvdbs_def_retr_params: GVDBsDefRetrParams | string) => void;
}

export interface GVDBsRetrParamsLoaded {
  isLoaded: boolean;
  setIsLoaded: (isLoaded: boolean) => void;
}
