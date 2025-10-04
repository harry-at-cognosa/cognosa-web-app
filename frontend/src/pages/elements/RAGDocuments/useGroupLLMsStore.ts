import { create } from "zustand";
import type { GroupLLMs } from "./groupLLMs";

interface GroupLLMsState {
  rows: GroupLLMs[];
  setRows: (rows: GroupLLMs[]) => void;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
}

export const useGroupLLMsStore = create<GroupLLMsState>((set) => ({
  rows: [],
  setRows: (rows) => set({ rows }),
  needReload: true,
  setNeedReload: (needReload: boolean) => set({ needReload }),
}));

interface GroupLLMsLastUsedState {
  gllms_id: number | null;
  setGLLMsID: (gllms_id: number | null) => void;
}

export const useGroupLLMsLastUsedStore = create<GroupLLMsLastUsedState>(
  (set) => ({
    gllms_id: null,
    setGLLMsID: (gllms_id) => set({ gllms_id }),
  })
);
