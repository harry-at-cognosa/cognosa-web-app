import { create } from "zustand";
import type { DocTasksShortItem } from "../../../models/docTasksShortItem";

const getGroupKey = (item: {
  created_at: string;
}): "Today" | "This week" | "Before" => {
  const itemDate = new Date(item.created_at);
  const now = new Date();

  // Check if it's today
  if (
    itemDate.getDate() === now.getDate() &&
    itemDate.getMonth() === now.getMonth() &&
    itemDate.getFullYear() === now.getFullYear()
  ) {
    return "Today";
  }

  // Check if it's within the last 7 days
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); // 7 days ago
  if (itemDate >= oneWeekAgo) {
    return "This week";
  }

  return "Before";
};

interface DocTasksShortState {
  rows: DocTasksShortItem[];
  setRows: (rows: DocTasksShortItem[]) => void;
  getTodayRows: () => DocTasksShortItem[];
  getWeekRows: () => DocTasksShortItem[];
  getBeforeRows: () => DocTasksShortItem[];
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
  deleteRow: (doc_task_id: number) => void;
}

export const useDocTasksShortStore = create<DocTasksShortState>((set, get) => ({
  rows: [],
  setRows: (rows) => set({ rows }),
  getTodayRows: () => {
    return get().rows.filter((item) => getGroupKey(item) === "Today");
  },
  getWeekRows: () => {
    return get().rows.filter((item) => getGroupKey(item) === "This week");
  },
  getBeforeRows: () => {
    return get().rows.filter((item) => getGroupKey(item) === "Before");
  },
  needReload: true,
  setNeedReload: (needReload: boolean) => set({ needReload }),
  deleteRow: (doc_task_id: number) =>
    set((state) => ({
      rows: state.rows.filter((item) => item.doc_task_id !== doc_task_id),
    })),
}));
