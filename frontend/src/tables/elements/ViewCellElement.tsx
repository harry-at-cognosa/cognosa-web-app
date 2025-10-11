import OnlyEnableCheck from "../CellRenders/OnlyEnableCheck";
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
  if (cellType === "bool_green")
    return <OnlyEnableCheck value={value}></OnlyEnableCheck>;
  if (cellType === "text") return <TextCell value={value}></TextCell>;
  return value?.toString();
}
