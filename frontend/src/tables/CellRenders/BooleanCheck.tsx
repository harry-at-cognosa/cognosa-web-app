import type { TableOptions, TableCellValue } from "../TableStoreFactory";

interface Props {
  table_options: TableOptions;
  col: string;
  value: TableCellValue;
}

export default function BooleanCheck({ table_options, col, value }: Props) {
  if (!table_options) return null;
  if (!value && table_options.read__hide_on_false.includes(col)) return null;
  if (value)
    return (
      <span
        style={{
          color: "green",
          fontSize: "1.2em",
          fontWeight: "bold",
        }}
      >
        ✓
      </span>
    );
  else
    return (
      <span
        style={{
          color: "red",
          fontSize: "1.2em",
          fontWeight: "bold",
        }}
      >
        X
      </span>
    );
}
