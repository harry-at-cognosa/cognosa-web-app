import { useDocTasksGVDBsRetrFiltersStore } from "./useDocTasksGVDBsRetrFiltersStore";
import { useDefaultGVDBsRetrFiltersStore } from "./useDefaultGVDBsRetrFiltersStore";

interface TableRow {
  key: string;
  rf_field_id: string;
  display: string;
  value: string;
  is_not: boolean;
}

/** Active filter values as read-only tags, with the NOT mark when the global NOT is on. */
export default function GVDBsRetrFiltersTable() {
  const defStore = useDefaultGVDBsRetrFiltersStore();
  const curStore = useDocTasksGVDBsRetrFiltersStore();
  if (!(defStore.isLoaded && defStore.rf_field_id__field)) return null;
  const data = curStore.getDict();
  if (!data) return null;
  const tableRows: TableRow[] = [];
  for (const { rf_field_id, values_list } of data.values) {
    const value = values_list.join(" | ");
    const display =
      defStore.rf_field_id__field[rf_field_id]?.title || rf_field_id;
    tableRows.push({
      key: "rft__" + rf_field_id,
      rf_field_id,
      display,
      value,
      is_not: data.global_not_value === true,
    });
  }
  if (!tableRows.length) return null;

  return (
    <div
      className="flex basis-full flex-wrap items-center gap-1.5"
      aria-label="Active retrieval filters"
    >
      {data.global_not_value === true ? (
        <span className="tag-not">NOT</span>
      ) : null}
      {tableRows.map((d) => (
        <span key={d.key} className="tag">
          {d.display}: <b>{d.value}</b>
        </span>
      ))}
    </div>
  );
}
