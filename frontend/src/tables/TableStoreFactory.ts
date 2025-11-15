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
  cu_required: boolean;
  cu_edit_msg: string;
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

interface ErrorColumnDetail {
  input: TableCellValue;
  loc: string[];
  msg: string;
  type: string;
}

export interface TableRowCreateResponse {
  result: string;
  total_created: number;
  detail?: ErrorColumnDetail[];
}

export interface TableRowUpdateResponse {
  result: string;
  total_updated: number;
  detail?: ErrorColumnDetail[];
}

export interface TableRowDeleteResponse {
  result: string;
  total_deleted: number;
  details?: ErrorColumnDetail[];
}

export interface TableStore {
  title: string;
  busy:
    | ""
    | "create"
    | "create_pending"
    | "read"
    | "update"
    | "update_pending"
    | "delete";
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
  editRowErrorMsg: Record<string, string>;
  editRowErrorMark: Record<string, boolean>;
  setEditRowErrorMark: (col: string, value: boolean) => void;
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
    editRowErrorMsg: {},
    editRowErrorMark: {},
    setEditRowErrorMark: (col: string, value: boolean) => {
      set({ editRowErrorMark: { ...get().editRowErrorMark, [col]: value } });
    },
    busyCreateOrUpdateDialog: false,
    setShowCreateOrUpdateDialog: (
      showCreateOrUpdateDialog: "" | "create" | "update",
      editRow: TableRow | null
    ) =>
      set({
        showCreateOrUpdateDialog,
        editRow,
        editRowErrorMsg: {},
        editRowErrorMark: {},
      }),
    setEditRow: (editRow: TableRow | null) => set({ editRow }),
    queryEditRow: async () => {
      if (get().busy) return;
      const showCreateOrUpdateDialog = get().showCreateOrUpdateDialog;
      if (!showCreateOrUpdateDialog) return;
      const valuesRow = get().editRow;
      if (!valuesRow) return;
      const isCreate = showCreateOrUpdateDialog === "create";
      set({
        busy: isCreate ? "create_pending" : "update_pending",
        error: null,
      });
      try {
        if (isCreate)
          await axiosClient.post<TableRowCreateResponse>(endpoint, valuesRow);
        else await axiosClient.put<TableRowUpdateResponse>(endpoint, valuesRow);
        if (afterEdit) await afterEdit(get);
        set({
          busy: "",
          editRow: null,
          editRowErrorMsg: {},
          editRowErrorMark: {},
          showCreateOrUpdateDialog: "",
          needReload: true,
        });
      } catch (err: any) {
        const detailList: ErrorColumnDetail[] | undefined =
          err.response?.data?.detail;
        set({
          busy: showCreateOrUpdateDialog,
        });
        if (detailList) {
          // validation errors
          const colList = Object.keys(valuesRow);
          const editRowErrorMsg: Record<string, string> = {};
          const editRowErrorMark: Record<string, boolean> = {};
          for (const detail of detailList) {
            for (const loc of detail.loc) {
              if (colList.includes(loc)) {
                editRowErrorMsg[loc] = detail.msg;
                editRowErrorMark[loc] = true;
                break;
              }
            }
          }
          set({ editRowErrorMsg, editRowErrorMark, busy: "" });
        } else {
          set({
            error: err.response?.data?.message || err.message,
          });
        }
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
