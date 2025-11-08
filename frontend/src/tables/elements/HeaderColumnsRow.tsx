import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";
import type { createTableStore } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";
import HeaderColumnOrderArrow from "./HeaderColumnOrderArrow";
import styles from "./HeaderColumnsRow.module.css";
import clsx from "clsx";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function HeaderColumnsRow({ useStore }: Props) {
  const { color } = useWebAppOptionsStore();
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
      {/* edit th */}
      {data.table_options.update__ask_columns.length ? (
        <th style={{ backgroundColor: color.c100 }}></th>
      ) : null}
      {/* visible columns display names */}
      {data.table_options.read__visible_columns.map((col) => (
        <th
          key={col}
          className={clsx(
            "text-nowrap",
            data.table_options.order_by__allow.includes(col)
              ? styles.sortableHeader
              : null
          )}
          style={{ backgroundColor: color.c100 }}
          onClick={() => {
            onHeaderClick(col);
          }}
        >
          <ColumnDisplayName data={data} col={col}></ColumnDisplayName>

          <HeaderColumnOrderArrow
            data={data}
            col={col}
            nextRequest={tableStore.nextRequest}
          ></HeaderColumnOrderArrow>
        </th>
      ))}
      {/* delete th */}
      {data.table_options.delete__ask_columns.length ? (
        <th style={{ backgroundColor: color.c100 }}></th>
      ) : null}
    </tr>
  );
}
