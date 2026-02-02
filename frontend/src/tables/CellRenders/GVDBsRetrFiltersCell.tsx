import type { GVDBsRetrFiltersSchema } from "../../components/GVDBsRetrFilters/types";
import type { TableCellValue } from "../TableStoreFactory";

interface Props {
  value: TableCellValue;
}

export default function GVDBsRetrFiltersCell({ value }: Props) {
  if (!value) return null;
  if (value === "{}") return "-";
  const data: GVDBsRetrFiltersSchema = JSON.parse(value.toString());

  return (
    <table className="mx-auto">
      <tbody>
        {data.global_not_enabled ? (
          <tr key={"global_not_enabled"}>
            <td>Global NOT</td>
          </tr>
        ) : null}
        {data.fields.map((f) => (
          <tr key={f.rf_field_id}>
            <td>{f.title}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
