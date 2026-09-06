import { Form } from "react-bootstrap";
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
    <tr style={{ textAlign: "center", verticalAlign: "middle" }}>
      <th className="bg-tc-100 p-1"></th>
      {data.table_options.read__visible_columns.map((col) => (
        <th key={"filter_" + col} className="bg-tc-100 p-1 fw-normal">
          {allow.includes(col) ? (
            <Form.Select
              size="sm"
              value={currentValue(col)}
              onChange={(e) => onChange(col, e.target.value)}
              title={"Filter: " + (data.columns[col]?.display || col)}
              style={{ minWidth: "5rem" }}
            >
              <option value="">All</option>
              {optionsFor(col).map((o) => (
                <option key={col + "_" + o.value} value={o.value}>
                  {o.name}
                </option>
              ))}
            </Form.Select>
          ) : null}
        </th>
      ))}
      {data.table_options.delete__ask_columns.length ? (
        <th className="bg-tc-100 p-1"></th>
      ) : null}
    </tr>
  );
}
