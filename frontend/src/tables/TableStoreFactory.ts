import axiosClient from "../api/axiosClient";
import { createResettableStore } from "../api/createResettableStore";

export interface TableRequest {
  name: string;
  limit: number;
  offset: number;
  order_by?: string;
  order_dir?: "asc" | "desc";
  filters?: Record<string, any>;
}

interface SelectOption {
  name: string;
  value: string | number;
}

export interface TableColumnData {
  display: string;
  type: string;
  default: string | number | boolean | null;
  select: SelectOption[] | null;
  min_width: string | null;
}

export interface TableOptions {
  title: string;
  pk: string;
  read__visible_columns: string[];
  read__hide_on_false: string[];
  create__ask_columns: string[];
  update__ask_columns: string[];
  delete__ask_columns: string[];
  order_by__allow: string[];
  add_values: Record<string, any>;
  default_limit: number;
  max_limit: number;
  select_limit: number[];
}

export type TableCellValue = string | number | boolean | null | undefined;
export type TableRow = Record<string, TableCellValue>;

export interface TableResponse {
  name: string;
  rows: TableRow[];
  columns: Record<string, TableColumnData>;
  table_options: TableOptions;
  order_by: string;
  order_dir: "asc" | "desc";
  total: number;
  limit: number;
  offset: number;
}

export interface TableRowCreateResponse {
  result: string;
  total_created: number;
}

export interface TableRowUpdateResponse {
  result: string;
  total_updated: number;
}

export interface TableRowDeleteResponse {
  result: string;
  total_deleted: number;
}

export interface TableStore {
  title: string;
  busy: "" | "create" | "read" | "update" | "delete";
  error: string | null;
  data: TableResponse | null;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
  nextRequest: TableRequest;
  queryTable: () => Promise<void>;
  setLimit: (newLimit: number) => void;
  setOffset: (newOffset: number) => void;

  readRow: TableRow | null;
  setReadRow: (askRead: TableRow | null) => void;

  showCreateOrUpdateDialog: "" | "create" | "update";
  editRow: TableRow | null;
  setShowCreateOrUpdateDialog: (
    showCreateOrUpdateDialog: "" | "create" | "update",
    editRow: TableRow | null
  ) => void;
  setEditRow: (editRow: TableRow | null) => void;
  queryEditRow: () => Promise<void>;

  deleteRow: TableRow | null;
  setDeleteRow: (askDelete: TableRow | null) => void;
  queryDeleteRow: () => Promise<void>;
}

interface createTableStoreProps {
  title: string;
  name: string;
  endpoint: string;
  afterRead?: (get: () => TableStore) => Promise<void>;
  afterEdit?: (get: () => TableStore) => Promise<void>;
  afterDelete?: (get: () => TableStore) => Promise<void>;
  order_by?: string;
  order_dir?: "asc" | "desc";
}

export function createTableStore({
  title,
  name,
  endpoint,
  afterRead,
  afterEdit,
  afterDelete,
  order_by,
  order_dir,
}: createTableStoreProps) {
  return createResettableStore<TableStore>((set, get) => ({
    title,
    busy: "",
    error: null,
    data: null,
    needReload: false,
    setNeedReload: (needReload) => set({ needReload }),
    nextRequest: { name, order_by, order_dir, limit: 0, offset: 0 },
    queryTable: async () => {
      if (get().busy) return;
      set({ busy: "read", error: null });
      try {
        const res = await axiosClient.post<TableResponse>(
          endpoint + "/query",
          get().nextRequest
        );
        set({
          data: res.data,
          nextRequest: {
            ...get().nextRequest,
            order_by: res.data.order_by,
            order_dir: res.data.order_dir,
            limit: res.data.limit,
            offset: res.data.offset,
          },
        });
        if (afterRead) await afterRead(get);
      } catch (err: any) {
        set({ error: err.response?.data?.message || err.message });
      } finally {
        set({ busy: "", needReload: false });
      }
    },
    setLimit: (newLimit: number) => {
      if (newLimit !== get().nextRequest.limit)
        set({
          nextRequest: { ...get().nextRequest, limit: newLimit, offset: 0 },
          needReload: true,
        });
    },
    setOffset: (newOffset: number) => {
      if (newOffset !== get().nextRequest.offset)
        set({
          nextRequest: { ...get().nextRequest, offset: newOffset },
          needReload: true,
        });
    },
    showCreateOrUpdateDialog: "",
    editRow: null,
    setShowCreateOrUpdateDialog: (
      showCreateOrUpdateDialog: "" | "create" | "update",
      editRow: TableRow | null
    ) => set({ showCreateOrUpdateDialog, editRow }),
    setEditRow: (editRow: TableRow | null) => set({ editRow }),
    queryEditRow: async () => {
      if (get().busy) return;
      const showCreateOrUpdateDialog = get().showCreateOrUpdateDialog;
      if (!showCreateOrUpdateDialog) return;
      set({ busy: showCreateOrUpdateDialog, error: null });
      try {
        if (showCreateOrUpdateDialog === "create")
          await axiosClient.post<TableRowCreateResponse>(
            endpoint,
            get().editRow
          );
        else
          await axiosClient.put<TableRowUpdateResponse>(
            endpoint,
            get().editRow
          );
        if (afterEdit) await afterEdit(get);
      } catch (err: any) {
        set({
          error: err.response?.data?.message || err.message,
        });
      } finally {
        set({
          busy: "",
          editRow: null,
          showCreateOrUpdateDialog: "",
          needReload: true,
        });
      }
    },
    readRow: null,
    setReadRow: (readRow: TableRow | null) => set({ readRow }),
    deleteRow: null,
    setDeleteRow: (deleteRow: TableRow | null) => set({ deleteRow }),
    queryDeleteRow: async () => {
      if (get().busy) return;
      const table_options = get().data?.table_options;
      if (!table_options) return;
      const rowToDelete = get().deleteRow;
      if (!rowToDelete) return;
      const pkColName = table_options.pk;
      const pkValue = rowToDelete[pkColName];
      if (pkValue === null || pkValue === undefined) return;
      set({ busy: "delete", error: null });
      try {
        await axiosClient.delete<TableRowDeleteResponse>(
          endpoint + "/" + pkValue.toString()
        );
        if (afterDelete) await afterDelete(get);
      } catch (err: any) {
        set({
          error: err.response?.data?.message || err.message,
        });
      } finally {
        set({ busy: "", deleteRow: null, needReload: true });
      }
    },
  }));
}
