import type { DocTasksGVDBsCfgState } from "../GVDBsRetrParams/types";

export interface GVDBsRetrFiltersHistoryEntry {
  global_not_value: boolean | null;
  rf_field_id__values: Record<string, string[]>;
}

export class GVDBsRetrFiltersHistory {
  // data: {doc_task_id: {gvdbs_id: GVDBsRetrFiltersHistoryEntry, ...}, ...}
  static data: Record<number, Record<number, GVDBsRetrFiltersHistoryEntry>> =
    {};
  static updateFromGVDBsCfgJSON(
    doc_task_id: number | null,
    gvdbs_id: number | null,
    gvdbs_cfg_json: DocTasksGVDBsCfgState | null,
  ) {
    const f = gvdbs_cfg_json?.filters;
    if (!f) return;
    const global_not_value =
      f.global_not_value === undefined ? null : f.global_not_value;
    const rf_field_id__values: Record<string, string[]> = {};
    for (const field of f.values) {
      rf_field_id__values[field.rf_field_id] = field.values_list;
    }
    GVDBsRetrFiltersHistory.update(
      doc_task_id,
      gvdbs_id,
      global_not_value,
      rf_field_id__values,
    );
  }
  static update(
    doc_task_id: number | null,
    gvdbs_id: number | null,
    global_not_value: boolean | null,
    rf_field_id__values: Record<string, string[]>,
  ) {
    if (!gvdbs_id || gvdbs_id === -1) return;
    if (!GVDBsRetrFiltersHistory.data[doc_task_id || 0])
      GVDBsRetrFiltersHistory.data[doc_task_id || 0] = {};
    GVDBsRetrFiltersHistory.data[doc_task_id || 0][gvdbs_id] = JSON.parse(
      JSON.stringify({ global_not_value, rf_field_id__values }),
    );
  }
  static get(
    doc_task_id: number | null,
    gvdbs_id: number | null,
  ): GVDBsRetrFiltersHistoryEntry | null {
    if (!gvdbs_id || gvdbs_id === -1) return null;
    return GVDBsRetrFiltersHistory.data[doc_task_id || 0]?.[gvdbs_id] || null;
  }
  static delete(doc_task_id: number | null, gvdbs_id: number | null): void {
    if (!gvdbs_id || gvdbs_id === -1) return;
    if (!GVDBsRetrFiltersHistory.data[doc_task_id || 0])
      GVDBsRetrFiltersHistory.data[doc_task_id || 0] = {};
    delete GVDBsRetrFiltersHistory.data[doc_task_id || 0][gvdbs_id];
  }
}
