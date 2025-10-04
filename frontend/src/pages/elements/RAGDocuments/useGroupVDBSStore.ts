import { create } from "zustand";
import type { GroupVDBs } from "./groupVDBs";

interface GroupVDBsState {
  rows: GroupVDBs[];
  setRows: (rows: GroupVDBs[]) => void;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
}

export const useGroupVDBsStore = create<GroupVDBsState>((set) => ({
  rows: [],
  setRows: (rows) => set({ rows }),
  needReload: true,
  setNeedReload: (needReload: boolean) => set({ needReload }),
}));

interface GroupVDBsLastUsedState {
  gvdbs_id: number | null;
  setGVDBsID: (gvdbs_id: number | null) => void;
}

export const useGroupVDBsLastUsedStore = create<GroupVDBsLastUsedState>(
  (set) => ({
    gvdbs_id: null,
    setGVDBsID: (gvdbs_id) => set({ gvdbs_id }),
  })
);
