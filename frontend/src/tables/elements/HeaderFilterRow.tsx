import { TableHead, TableRow } from "@/components/ui/table";
import { Sel } from "@/components/Sel";
import type { createTableStore } from "../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

// Feature 202: one row of compact selects under the column headers, only for
// columns listed in table_options.filter__allow.
export default function HeaderFilterRow({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;
  if (!data) return null;
  const allow = data.table_options.filter__allow || [];
  if (!allow.length) return null;
  const filters = tableStore.nextRequest.filters || {};

  function optionsFor(col: string): { name: string; value: string }[] {
    const column = data!.columns[col];
    if (!column) return [];
    if (column.type === "boolean")
      return [
        { name: "Yes", value: "true" },
        { name: "No", value: "false" },
      ];
    if (column.type === "group_id_name") {
      const map: Record<string, string> =
        data!.table_options.add_values["group_id_name"] || {};
      return Object.keys(map)
        .map((k) => Number(k))
        .sort((a, b) => a - b)
        .map((id) => ({ name: map[id], value: String(id) }));
    }
    if (column.select)
      return column.select.map((o) => ({ name: o.name, value: String(o.value) }));
    return [];
  }

  function currentValue(col: string): string {
    const v = filters[col];
    return v === undefined || v === null ? "" : String(v);
  }

  // raw is "" for "All" (Sel maps its empty item back to "")
  function onChange(col: string, raw: string) {
    if (tableStore.busy) return;
    const column = data!.columns[col];
    if (raw === "") return tableStore.setFilter(col, null);
    if (column.type === "boolean") return tableStore.setFilter(col, raw === "true");
    if (column.type === "group_id_name" || column.type === "number")
      return tableStore.setFilter(col, Number(raw));
    tableStore.setFilter(col, raw);
  }

  return (
    <TableRow className="border-b border-line">
      <TableHead className="pt-0"></TableHead>
      {data.table_options.read__visible_columns.map((col) => (
        <TableHead key={"filter_" + col} className="pt-0 pb-2 font-normal">
          {allow.includes(col) ? (
            <Sel
              size="sm"
              value={currentValue(col)}
              onChange={(v) => onChange(col, v)}
              emptyLabel="All"
              label={"Filter: " + (data.columns[col]?.display || col)}
              options={optionsFor(col).map((o) => ({
                value: o.value,
                label: o.name,
              }))}
              className="h-[30px]! min-w-20 rounded-full text-[13px] text-ink"
            />
          ) : null}
        </TableHead>
      ))}
      {data.table_options.delete__ask_columns.length ? (
        <TableHead className="pt-0"></TableHead>
      ) : null}
    </TableRow>
  );
}
