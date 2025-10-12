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
  create__allow: boolean;
  read__hide_on_false: string[];
  update__allow: boolean;
  delete__allow: boolean;
  delete__ask_columns: string[];
  order_by__allow: string[];
}

export type TableCellValue = string | number | boolean | null | undefined;
export type TableRow = Record<string, TableCellValue>;

export interface TableResponse {
  name: string;
  rows: TableRow[];
  columns: Record<string, TableColumnData>;
  table_options: TableOptions;
  total?: number;
}

export interface TableRowDeleteResponse {
  result: string;
  total_deleted: number;
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
  askDelete: TableRow | null;
  setAskDelete: (askDelete: TableRow | null) => void;
  deleting: boolean;
  deleteRow: () => Promise<void>;
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
      set({ loading: true, error: null });
      try {
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
    askDelete: null,
    setAskDelete: (askDelete: TableRow | null) => set({ askDelete }),
    deleting: false,
    deleteRow: async () => {
      const table_options = get().data?.table_options;
      if (!table_options) return;
      const rowToDelete = get().askDelete;
      if (!rowToDelete) return;
      const pkColName = table_options.pk;
      const pkValue = rowToDelete[pkColName];
      if (pkValue === null || pkValue === undefined) return;
      set({ deleting: true, error: null });
      try {
        await axiosClient.delete<TableRowDeleteResponse>(
          endpoint + "/" + pkValue.toString()
        );
      } catch (err: any) {
        set({
          error: err.response?.data?.message || err.message,
        });
      } finally {
        set({ deleting: false, askDelete: null, needReload: true });
      }
    },
  }));
}
