import BooleanCheck from "../CellRenders/BooleanCheck";
import TextCell from "../CellRenders/TextCell";
import type { TableResponse, TableRow } from "../TableStoreFactory";

interface Props {
  data: TableResponse | null;
  row: TableRow;
  col: string;
}

export default function ViewCellElement({ data, row, col }: Props) {
  if (!data) return null;
  const value = row[col];
  const cellType = data.columns[col].type;
  const add_values = data.table_options.add_values;
  if (cellType === "boolean")
    return (
      <td key={col}>
        <BooleanCheck
          table_options={data.table_options}
          col={col}
          value={value}
        ></BooleanCheck>
      </td>
    );
  if (cellType === "text")
    return (
      <td key={col}>
        <TextCell value={value}></TextCell>
      </td>
    );
  if (cellType === "group_id_name") {
    const group_id_name: Record<number, string> = add_values["group_id_name"];
    return <td key={col}>{group_id_name[Number(value)]}</td>;
  }
  if (["gllms_status", "gvdbs_status"].includes(cellType)) {
    const cellText =
      row["gllms_status_text"] || row["gvdbs_status_text"] || "<Pending>";
    return (
      <td key={col} className={"table-" + value}>
        {cellText}
      </td>
    );
  }
  return <td key={col}>{value?.toString()}</td>;
}
