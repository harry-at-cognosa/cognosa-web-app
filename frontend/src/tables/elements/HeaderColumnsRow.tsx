import type { createTableStore } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function HeaderColumnsRow({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;
  if (!data) return null;

  return (
    <tr style={{ textAlign: "center", verticalAlign: "middle" }}>
      {/* edit th */}
      {data.table_options.update__ask_columns.length ? <th></th> : null}
      {/* visible columns display names */}
      {data.table_options.read__visible_columns.map((col) => (
        <th key={col} className="text-nowrap">
          <ColumnDisplayName data={data} col={col}></ColumnDisplayName>
        </th>
      ))}
      {/* delete th */}
      {data.table_options.delete__ask_columns.length ? <th></th> : null}
    </tr>
  );
}
