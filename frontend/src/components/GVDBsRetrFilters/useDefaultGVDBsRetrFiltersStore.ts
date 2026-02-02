import { create } from "zustand";
import type {
  GVDBsRetrFiltersField,
  GVDBsRetrFiltersLoaded,
  GVDBsRetrFiltersSchema,
  GVDBsRetrFiltersState,
} from "./types";

interface defState {
  rf_field_id__field: Record<string, GVDBsRetrFiltersField> | null;
}

export const useDefaultGVDBsRetrFiltersStore = create<
  GVDBsRetrFiltersState & GVDBsRetrFiltersLoaded & defState
>((set) => ({
  // GVDBsRetrFiltersState
  global_not_enabled: null,
  fields: null,
  rf_field_id__field: null,
  setDataFromString: (gvdbs_retr_filters: string) => {
    try {
      const parsed: GVDBsRetrFiltersSchema = JSON.parse(gvdbs_retr_filters);
      let rf_field_id__field: Record<string, GVDBsRetrFiltersField> | null =
        null;
      if (parsed.fields) {
        rf_field_id__field = {};
        for (const field of parsed.fields) {
          rf_field_id__field[field.rf_field_id] = field;
        }
      }
      set({
        global_not_enabled: parsed.global_not_enabled || false,
        fields: parsed.fields || null,
        rf_field_id__field: rf_field_id__field,
        isLoaded: true,
      });
    } catch (error) {
      console.error("setDataFromString->gvdbs_retr_filters:", error);
    }
  },

  // GVDBsRetrFiltersLoaded
  isLoaded: false,
  setIsLoaded: (isLoaded: boolean) => set({ isLoaded }),
}));
