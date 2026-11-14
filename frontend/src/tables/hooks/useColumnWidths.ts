import { create } from "zustand";

// User-set column widths in px, per table name and column. Kept in this
// browser's localStorage, so they survive a reload and a logout; a table
// renders with its default widths when nothing is stored.

type Widths = Record<string, Record<string, number>>;

const STORAGE_KEY = "cwa_table_column_widths";
export const MIN_COLUMN_WIDTH = 60;

function load(): Widths {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function save(widths: Widths) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(widths));
  } catch {
    // storage unavailable: widths last for this page load only
  }
}

interface ColumnWidthsState {
  widths: Widths;
  setWidth: (table: string, col: string, width: number) => void;
  resetWidth: (table: string, col: string) => void;
  persist: () => void;
}

export const useColumnWidths = create<ColumnWidthsState>((set, get) => ({
  widths: load(),
  setWidth: (table, col, width) =>
    set((state) => ({
      widths: {
        ...state.widths,
        [table]: {
          ...state.widths[table],
          [col]: Math.max(MIN_COLUMN_WIDTH, Math.round(width)),
        },
      },
    })),
  resetWidth: (table, col) => {
    const forTable = { ...get().widths[table] };
    delete forTable[col];
    set((state) => ({ widths: { ...state.widths, [table]: forTable } }));
    save(get().widths);
  },
  persist: () => save(get().widths),
}));
