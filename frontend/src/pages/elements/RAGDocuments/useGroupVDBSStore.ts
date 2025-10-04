import { create } from "zustand";
import type { GroupVDBS } from "./groupVDBS";

interface GroupVDBSState {
  rows: GroupVDBS[];
  setRows: (rows: GroupVDBS[]) => void;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
}

export const useGroupVDBSStore = create<GroupVDBSState>((set) => ({
  rows: [],
  setRows: (rows) => set({ rows }),
  needReload: true,
  setNeedReload: (needReload: boolean) => set({ needReload }),
}));

interface GroupVDBSLastUsedState {
  gvdbs_id: number | null;
  setGVDBSID: (gvdbs_id: number | null) => void;
}

export const useGroupVDBSLastUsedStore = create<GroupVDBSLastUsedState>(
  (set) => ({
    gvdbs_id: null,
    setGVDBSID: (gvdbs_id) => set({ gvdbs_id }),
  })
);
