import { create } from "zustand";
import type {
  DocTasksGVDBsRetrFiltersRequest,
  GVDBsRetrFiltersSchema,
  GVDBsRetrFiltersValuesEntry,
} from "./types";
import {
  GVDBsRetrFiltersHistory,
  type GVDBsRetrFiltersHistoryEntry,
} from "./history";

interface State {
  isLoaded: boolean;
  defState: GVDBsRetrFiltersSchema | null;
  global_not_value: boolean | null;
  rf_field_id__values: Record<string, string[]>;
  getDict: () => DocTasksGVDBsRetrFiltersRequest | null;
  initData: (
    defState: GVDBsRetrFiltersSchema,
    global_not_value: boolean | null,
    rf_field_id__values: Record<string, string[]>,
  ) => void;
  reset: () => void;
  loadFromRFHistory: (
    doc_task_id: number | null,
    gvdbs_id: number,
    defState: GVDBsRetrFiltersSchema,
  ) => void;
}

export const useDocTasksGVDBsRetrFiltersStore = create<State>((set, get) => ({
  isLoaded: false,
  defState: null,
  global_not_value: null,
  rf_field_id__values: {},
  getDict: () => {
    const defState = get().defState;
    const global_not_value = get().global_not_value;
    const rf_field_id__values = get().rf_field_id__values;
    if (!defState) return null;
    const newValues: GVDBsRetrFiltersValuesEntry[] = [];
    for (const [rf_field_id, valueList] of Object.entries(
      rf_field_id__values,
    )) {
      if (!valueList || !valueList.length) continue;
      const valueListTrimmed = valueList.filter((value) => value.trim());
      if (!valueListTrimmed.length) continue;
      newValues.push({
        rf_field_id,
        values_list: valueListTrimmed,
      });
    }
    if (!newValues.length) return null;
    if (global_not_value === null) return { values: newValues };
    return { global_not_value, values: newValues };
  },
  initData: (
    defState: GVDBsRetrFiltersSchema,
    global_not_value: boolean | null,
    rf_field_id__values: Record<string, string[]>,
  ) => {
    set({ defState: JSON.parse(JSON.stringify(defState)) });
    if (defState.global_not_enabled)
      set({ global_not_value: global_not_value || false });
    else set({ global_not_value: null });
    // make copy of value-lists for keys existing in defState
    const newValues: Record<string, string[]> = {};
    for (const { rf_field_id } of defState.fields) {
      const newValueList = rf_field_id__values[rf_field_id]
        ? [...rf_field_id__values[rf_field_id]]
        : [];
      newValues[rf_field_id] = newValueList.filter((value) => value.trim());
    }
    set({
      rf_field_id__values: newValues,
      isLoaded: true,
    });
  },
  reset: () =>
    set({ isLoaded: false, global_not_value: null, rf_field_id__values: {} }),
  loadFromRFHistory: (
    doc_task_id: number | null,
    gvdbs_id: number,
    defState: GVDBsRetrFiltersSchema,
  ) => {
    set({ defState: JSON.parse(JSON.stringify(defState)) });
    set({ isLoaded: true });
    const history = GVDBsRetrFiltersHistory.get(doc_task_id, gvdbs_id);
    if (!history) {
      set({ global_not_value: null, rf_field_id__values: {} });
      return;
    }
    const f: GVDBsRetrFiltersHistoryEntry = JSON.parse(JSON.stringify(history));
    if (defState.global_not_enabled)
      set({ global_not_value: f.global_not_value || false });
    else set({ global_not_value: null });
    // make copy of value-lists for keys existing in defState
    const newValues: Record<string, string[]> = {};
    for (const { rf_field_id } of defState.fields) {
      const newValueList = f.rf_field_id__values[rf_field_id]
        ? [...f.rf_field_id__values[rf_field_id]]
        : [];
      newValues[rf_field_id] = newValueList.filter((value) => value.trim());
    }
    set({ rf_field_id__values: newValues });
  },
}));
