import { create } from "zustand";
import axiosClient from "../api/axiosClient";

export interface TableRequest {
  name: string;
  limit?: number;
  offset?: number;
  order_by?: string;
  order_dir?: "asc" | "desc";
  filters?: Record<string, any>;
}

export interface TableColumnData {
  display: string;
  seqn: number;
  type: string;
}

export interface TableOptions {
  title: string;
  pk: string;
  allow_add: boolean;
  allow_update: boolean;
  allow_delete: boolean;
  delete_ask_column: string;
}

export interface TableResponse {
  name: string;
  rows: Record<string, any>[];
  columns: Record<string, TableColumnData>;
  table_options: TableOptions;
  total?: number;
}

export interface TableStore {
  loading: boolean;
  error: string | null;
  data: TableResponse | null;
  visible_columns: string[];
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
  nextRequest: TableRequest;
  queryTable: () => Promise<void>;
}

interface createTableStoreProps {
  name: string;
  endpoint: string;
}

export function createTableStore({ name, endpoint }: createTableStoreProps) {
  return create<TableStore>((set, get) => ({
    loading: false,
    error: null,
    data: null,
    visible_columns: [], // column names, sort by seqn
    needReload: false,
    setNeedReload: (needReload) => set({ needReload }),
    nextRequest: { name },
    queryTable: async () => {
      try {
        set({ loading: true, error: null });
        const res = await axiosClient.post<TableResponse>(
          endpoint + "/query",
          get().nextRequest
        );
        set({
          data: res.data,
          visible_columns: Object.keys(res.data.columns)
            .filter((col) => res.data.columns[col].seqn !== null) // seqn = null means invisible
            .sort(
              (a, b) => res.data.columns[a].seqn - res.data.columns[b].seqn
            ),
          loading: false,
        });
      } catch (err: any) {
        set({
          error: err.response?.data?.message || err.message,
          loading: false,
        });
      } finally {
        set({ needReload: false });
      }
    },
  }));
}
