import { create } from "zustand";
import type { GVDBsRetrFiltersSchema } from "./types";

interface ModalState {
  isLoaded: boolean;
  global_not_value: boolean | null;
  setGlobalNotValue: (global_not_value: boolean | null) => void;
  rf_field_id__values: Record<string, string[]>;
  setValues: (rf_field_id__values: Record<string, string[]>) => void;
  getJSON: () => string | null;
  initData: (
    defState: GVDBsRetrFiltersSchema,
    global_not_value: boolean | null,
    rf_field_id__values: Record<string, string[]>,
  ) => void;
  reset: () => void;
}

export const useModalGVDBsRetrFiltersStore = create<ModalState>((set, get) => ({
  isLoaded: false,
  global_not_value: null,
  rf_field_id__values: {},
  setGlobalNotValue: (global_not_value: boolean | null) =>
    set({ global_not_value }),
  setValues: (rf_field_id__values: Record<string, string[]>) =>
    set({ rf_field_id__values }),
  getJSON: () => {
    const global_not_value = get().global_not_value;
    const rf_field_id__values = get().rf_field_id__values;
    return JSON.stringify({ global_not_value, rf_field_id__values });
  },
  initData: (
    defState: GVDBsRetrFiltersSchema,
    global_not_value: boolean | null,
    rf_field_id__values: Record<string, string[]>,
  ) => {
    if (defState.global_not_enabled)
      set({ global_not_value: global_not_value || false });
    else set({ global_not_value: null });
    // make copy of value-lists for keys existing in defState
    const newValues: Record<string, string[]> = {};
    for (const { rf_field_id } of defState.fields) {
      newValues[rf_field_id] = rf_field_id__values[rf_field_id]
        ? [...rf_field_id__values[rf_field_id]]
        : [];
    }
    set({
      rf_field_id__values: newValues,
      isLoaded: true,
    });
  },
  reset: () =>
    set({ isLoaded: false, global_not_value: null, rf_field_id__values: {} }),
}));
