import getColor from "../../api/getColor";
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
  const pk_value_str = (row[data.table_options.pk] || -1).toString();
  const key = "td__" + pk_value_str + "__" + col;
  const value = row[col];
  const value_str = value?.toString() || "";
  const cellType = data.columns[col].type;
  const add_values = data.table_options.add_values;

  if (cellType === "boolean")
    return (
      <td key={key}>
        <BooleanCheck
          table_options={data.table_options}
          col={col}
          value={value}
        ></BooleanCheck>
      </td>
    );
  if (cellType === "text") {
    if (!value) return <td key={key}></td>;
    return (
      <td key={key}>
        <TextCell value={value}></TextCell>
      </td>
    );
  }
  if (cellType === "group_id_name") {
    const group_id_name: Record<number, string> = add_values["group_id_name"];
    return <td key={key}>{group_id_name[Number(value)]}</td>;
  }
  if (cellType === "user_id_name") {
    const user_id_name: Record<number, string> = add_values["user_id_name"];
    return <td key={key}>{user_id_name[Number(value)]}</td>;
  }
  if (["gllms_status", "gvdbs_status"].includes(cellType)) {
    const cellText =
      row["gllms_status_text"] || row["gvdbs_status_text"] || "<Pending>";
    return (
      <td key={key} className={"table-" + value}>
        {cellText}
      </td>
    );
  }
  if (cellType === "api_settings_value") {
    if (pk_value_str === "webapp_main_color")
      return (
        <td
          key={key}
          className="fw-bold"
          style={{
            backgroundColor: getColor(value_str, 300),
          }}
        >
          {value}
        </td>
      );
    return (
      <td key={key}>
        <TextCell value={value} rows={2}></TextCell>
      </td>
    );
  }
  return <td key={key}>{value_str}</td>;
}
