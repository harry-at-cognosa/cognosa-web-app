import type { TableResponse } from "../TableStoreFactory";

interface Props {
  nameType: "table" | "dialog";
  data: TableResponse | null;
  col: string;
}

export default function ColumnDisplayName({ nameType, data, col }: Props) {
  if (!data) return null;
  let displayName = data.columns[col].display || col;
  if (nameType === "dialog") return displayName;
  let lines = displayName.split("\n");
  if (lines.length <= 1) return <span>{displayName}</span>;
  return (
    <span>
      {lines.map((x, i) => (
        <div key={i}>{x}</div>
      ))}
    </span>
  );
}
