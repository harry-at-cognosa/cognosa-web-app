import { TableHead, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { createTableStore } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";
import HeaderColumnOrderArrow from "./HeaderColumnOrderArrow";
import styles from "./HeaderColumnsRow.module.css";
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
  const hasFilterRow = !!(data.table_options.filter__allow || []).length;
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
    <TableRow
      className={cn(
        "border-t border-line-soft",
        hasFilterRow ? "border-b-0" : "border-b border-line",
      )}
    >
      {/* view/edit th */}
      <TableHead>
        <span className="sr-only">
          {data.table_options.update__ask_columns.length ? "Edit" : "View"}
        </span>
      </TableHead>
      {/* visible columns display names */}
      {data.table_options.read__visible_columns.map((col) => {
        const sortable = data.table_options.order_by__allow.includes(col);
        const sorted = tableStore.nextRequest.order_by === col;
        return (
          <TableHead
            key={col}
            aria-sort={
              sortable && sorted
                ? tableStore.nextRequest.order_dir === "desc"
                  ? "descending"
                  : "ascending"
                : undefined
            }
            className={cn(
              sortable ? styles.sortableHeader : null,
              resizeAllow.includes(col) ? styles.resizableHeader : null,
            )}
            style={widthStyle(col)}
            onClick={() => {
              onHeaderClick(col);
            }}
          >
            {sortable ? (
              // the click is handled by the header cell, as in v1.0.1
              <button
                type="button"
                className={cn(
                  styles.sortButton,
                  sorted ? styles.sortButtonActive : null,
                )}
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
              </button>
            ) : (
              <ColumnDisplayName
                nameType="table"
                data={data}
                col={col}
              ></ColumnDisplayName>
            )}
            {resizeAllow.includes(col) ? (
              <ColumnResizeHandle table={data.name} col={col} />
            ) : null}
          </TableHead>
        );
      })}
      {/* delete th */}
      {data.table_options.delete__ask_columns.length ? (
        <TableHead>
          <span className="sr-only">Delete</span>
        </TableHead>
      ) : null}
    </TableRow>
  );
}
