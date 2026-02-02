import { Container, Table } from "react-bootstrap";
import { useDocTasksGVDBsRetrFiltersStore } from "./useDocTasksGVDBsRetrFiltersStore";
import { useDefaultGVDBsRetrFiltersStore } from "./useDefaultGVDBsRetrFiltersStore";

interface TableRow {
  key: string;
  rf_field_id: string;
  display: string;
  value: string;
  is_not: boolean;
}

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
      defStore.rf_field_id__field[rf_field_id].title || rf_field_id;
    tableRows.push({
      key: "rft__" + rf_field_id,
      rf_field_id,
      display,
      value,
      is_not: data.global_not_value === true,
    });
  }

  return (
    <Container>
      <Table bordered>
        <tbody>
          {tableRows.map((d) => (
            <tr key={d.key}>
              <th
                className={"text-nowrap py-0"}
                style={{ width: "1%", backgroundColor: "#fff0" }}
              >
                {d.display}
              </th>
              <th className="py-0" style={{ backgroundColor: "#fff0" }}>
                {d.is_not ? (
                  <span className="me-2 pb-1" style={{ color: "#e00000" }}>
                    NOT:
                  </span>
                ) : null}
                {d.value}
              </th>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
}
