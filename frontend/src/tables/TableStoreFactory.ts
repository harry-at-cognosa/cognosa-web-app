import { create } from "zustand";
import axiosClient from "../api/axiosClient";

export interface TableRequest {
  name: string;
  limit?: number;
  offset?: number;
  orderBy?: string;
  orderDir?: "asc" | "desc";
  filters?: Record<string, any>;
}

export interface TableResponse {
  name: string;
  pk: string;
  rows: Record<string, any>[];
  columns: Record<string, Record<string, any>>;
  total?: number;
}

export interface TableStore {
  loading: boolean;
  error: string | null;
  data: TableResponse | null;
  fetchTable: (endpoint: string, request: TableRequest) => Promise<void>;
}

export function createTableStore() {
  return create<TableStore>((set) => ({
    loading: false,
    error: null,
    data: null,

    fetchTable: async (endpoint, request) => {
      try {
        set({ loading: true, error: null });
        const res = await axiosClient.post<TableResponse>(endpoint, request);
        set({ data: res.data, loading: false });
      } catch (err: any) {
        set({
          error: err.response?.data?.message || err.message,
          loading: false,
        });
      }
    },
  }));
}
