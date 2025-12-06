import type { createTableStore } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";
import HeaderColumnOrderArrow from "./HeaderColumnOrderArrow";
import styles from "./HeaderColumnsRow.module.css";
import clsx from "clsx";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function HeaderColumnsRow({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;
  if (!data) return null;
  async function onHeaderClick(col: string) {
    if (!data?.table_options.order_by__allow.includes(col)) return;
    if (tableStore.busy) return;
    const order_dir =
      tableStore.nextRequest.order_by === col
        ? tableStore.nextRequest.order_dir === "desc"
          ? "asc"
          : "desc"
        : "asc";
    tableStore.nextRequest = {
      ...tableStore.nextRequest,
      order_by: col,
      order_dir: order_dir,
    };
    await tableStore.queryTable();
  }

  return (
    <tr
      style={{
        textAlign: "center",
        verticalAlign: "middle",
      }}
    >
      {/* view/edit th */}
      <th className="bg-tc-100"></th>
      {/* visible columns display names */}
      {data.table_options.read__visible_columns.map((col) => (
        <th
          key={col}
          className={clsx(
            "text-nowrap",
            tableStore.nextRequest.order_by === col ? "bg-tc-300" : "bg-tc-100",
            data.table_options.order_by__allow.includes(col)
              ? styles.sortableHeader
              : null
          )}
          style={{ minWidth: data.columns[col].min_width || "" }}
          onClick={() => {
            onHeaderClick(col);
          }}
        >
          <ColumnDisplayName
            nameType="table"
            data={data}
            col={col}
          ></ColumnDisplayName>

          <HeaderColumnOrderArrow
            data={data}
            col={col}
            nextRequest={tableStore.nextRequest}
          ></HeaderColumnOrderArrow>
        </th>
      ))}
      {/* delete th */}
      {data.table_options.delete__ask_columns.length ? (
        <th className="bg-tc-100"></th>
      ) : null}
    </tr>
  );
}
