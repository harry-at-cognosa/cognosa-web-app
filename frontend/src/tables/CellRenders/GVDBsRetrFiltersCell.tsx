import { Table } from "react-bootstrap";
import type { GVDBsRetrFiltersSchema } from "../../components/GVDBsRetrFilters/types";
import type { TableCellValue } from "../TableStoreFactory";
import { XCircle } from "react-bootstrap-icons";

interface Props {
  value: TableCellValue;
}

export default function GVDBsRetrFiltersCell({ value }: Props) {
  if (!value) return null;
  if (value === "{}") return "-";
  const data: GVDBsRetrFiltersSchema = JSON.parse(value.toString());

  return (
    <Table bordered className="mx-auto mb-0">
      <tbody>
        {data.global_not_enabled ? (
          <tr key={"global_not_enabled"} className="p-0">
            <td className="p-0">
              Global NOT <XCircle style={{ paddingBottom: "2px" }} />
            </td>
          </tr>
        ) : null}
        {data.fields.map((f) => (
          <tr key={f.rf_field_id} className="p-0">
            <td className="p-0">{f.title}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
}
