import type { createTableStore } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";
import HeaderColumnOrderArrow from "./HeaderColumnOrderArrow";
import styles from "./HeaderColumnsRow.module.css";
import clsx from "clsx";
import ColumnResizeHandle from "./ColumnResizeHandle";
import { useColumnWidths } from "../hooks/useColumnWidths";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function HeaderColumnsRow({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;
  const userWidths = useColumnWidths((state) => state.widths);
  if (!data) return null;
  const tableWidths = userWidths[data.name] || {};
  const resizeAllow = data.table_options.resize__allow || [];
  // a user-set width wins over the column's default width / min width
  function widthStyle(col: string) {
    const px = tableWidths[col];
    if (px) return { width: px + "px", minWidth: px + "px" };
    return {
      width: data!.columns[col].width || undefined,
      minWidth: data!.columns[col].min_width || "",
    };
  }
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
              : null,
            resizeAllow.includes(col) ? styles.resizableHeader : null
          )}
          style={widthStyle(col)}
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
          {resizeAllow.includes(col) ? (
            <ColumnResizeHandle table={data.name} col={col} />
          ) : null}
        </th>
      ))}
      {/* delete th */}
      {data.table_options.delete__ask_columns.length ? (
        <th className="bg-tc-100"></th>
      ) : null}
    </tr>
  );
}
