import type { DocTasksGVDBsRetrFiltersRequest } from "./types";

interface RetrFiltersShortTableRow {
  global_not: boolean;
  short_title: string;
  value: string;
}
export function getRetrFiltersShortTableFromJSONStr(
  jsonStr: string,
): RetrFiltersShortTableRow[] | null {
  try {
    const d = JSON.parse(jsonStr);
    const f = d["filters"] as DocTasksGVDBsRetrFiltersRequest;
    if (!f) return null;
    if (!f.values) return null;
    const rows: RetrFiltersShortTableRow[] = [];
    for (const v_row of f.values) {
      rows.push({
        global_not: f.global_not_value || false,
        short_title: v_row.short_title || "",
        value: v_row.values_list.join(" | "),
      });
    }
    return rows;
  } catch {
    return null;
  }
}
