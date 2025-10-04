import { create } from "zustand";
import type { groupContext } from "../../../models/groupContext";

interface ContextListState {
  rows: groupContext[];
  setRows: (rows: groupContext[]) => void;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
}

export const useContextListStore = create<ContextListState>((set) => ({
  rows: [],
  setRows: (rows) => set({ rows }),
  needReload: true,
  setNeedReload: (needReload: boolean) => set({ needReload }),
}));

interface ContextLastUsedState {
  gc_id: number | null;
  setGCID: (gc_id: number | null) => void;
}

export const useContextListLastUsedStore = create<ContextLastUsedState>(
  (set) => ({
    gc_id: null,
    setGCID: (gc_id) => set({ gc_id }),
  })
);
