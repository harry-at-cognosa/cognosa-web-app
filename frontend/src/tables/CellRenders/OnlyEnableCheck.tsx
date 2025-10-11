import type { TableCellValue } from "../TableStoreFactory";

interface Props {
  value: TableCellValue;
}

export default function OnlyEnableCheck({ value }: Props) {
  if (!value) {
    return null;
  }

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
}
