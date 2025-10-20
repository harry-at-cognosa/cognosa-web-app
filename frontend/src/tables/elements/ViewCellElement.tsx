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
      <BooleanCheck
        table_options={data.table_options}
        col={col}
        value={value}
      ></BooleanCheck>
    );
  if (cellType === "text") return <TextCell value={value}></TextCell>;
  if (cellType === "group_id_name") {
    const group_id_name: Record<number, string> = add_values["group_id_name"];
    return group_id_name[Number(value)];
  }
  return value?.toString();
}
