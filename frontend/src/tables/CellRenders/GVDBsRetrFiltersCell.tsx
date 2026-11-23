import { CircleX } from "lucide-react";
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
    <table className="border-collapse text-[13px] leading-snug">
      <tbody>
        {data.global_not_enabled ? (
          <tr key={"global_not_enabled"}>
            <td className="border border-line px-2 py-px whitespace-nowrap">
              Global NOT{" "}
              <CircleX className="mb-0.5 inline-block size-3.5" aria-hidden />
            </td>
          </tr>
        ) : null}
        {data.fields.map((f) => (
          <tr key={f.rf_field_id}>
            <td className="border border-line px-2 py-px whitespace-nowrap">
              {f.title}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
