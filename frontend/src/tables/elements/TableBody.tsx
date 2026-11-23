import { X } from "lucide-react";
import { TableCell, TableRow } from "@/components/ui/table";
import ViewCellElement from "./ViewCellElement";
import UpdateRowButton from "./UpdateRowButton";
import ReadRowButton from "./ReadRowButton";
import type { createTableStore } from "../TableStoreFactory";
import { BusyCell } from "../CellRenders/BusyCell";
import { useLayoutEffect, useRef } from "react";
import { fixTextareaHeights } from "../functions/fixTextareaHeights";
import { useColumnWidths } from "../hooks/useColumnWidths";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableBody({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;
  const tbodyRef = useRef<HTMLTableSectionElement | null>(null);
  // text reflows when a column is resized, so the row heights change
  const userWidths = useColumnWidths((state) => state.widths);
  if (!data) return null;
  const isBusy = tableStore.busy === "read";
  useLayoutEffect(() => {
    if (!tbodyRef.current) return;
    fixTextareaHeights(tbodyRef.current);
  }, [
    data.rows,
    data.table_options.read__visible_columns,
    tableStore.busy,
    userWidths,
  ]);
  return (
    <tbody ref={tbodyRef} className="[&_tr:last-child]:border-0">
      {data.rows.map((row) => (
        <TableRow
          key={row[data.table_options.pk]?.toString()}
          className="hover:bg-(--row-hover)"
        >
          {/* view/edit button cell */}
          <TableCell
            key={row[data.table_options.pk]?.toString() + "__edit"}
            className="relative w-px pr-0"
          >
            <div>
              {data.table_options.update__ask_columns.length ? (
                <UpdateRowButton
                  row={row}
                  useStore={useStore}
                ></UpdateRowButton>
              ) : (
                <ReadRowButton row={row} useStore={useStore}></ReadRowButton>
              )}
            </div>
            <BusyCell isBusy={isBusy} />
          </TableCell>
          {/* visible columns */}
          {tableStore.data?.table_options?.read__visible_columns.map((col) => (
            <ViewCellElement
              useStore={useStore}
              row={row}
              col={col}
              key={row[data.table_options.pk]?.toString() + "__vce__" + col}
              isBusy={isBusy}
            ></ViewCellElement>
          ))}
          {/* delete button cell */}
          {data.table_options.delete__ask_columns.length ? (
            <TableCell
              key={row[data.table_options.pk]?.toString() + "__delete"}
              className="relative w-px px-1.5"
            >
              <div>
                <button
                  type="button"
                  className="x-btn"
                  aria-label="Delete"
                  title="Delete"
                  onClick={() => tableStore.setDeleteRow(row)}
                >
                  <X className="size-4" />
                </button>
              </div>
              <BusyCell isBusy={isBusy} />
            </TableCell>
          ) : null}
        </TableRow>
      ))}
    </tbody>
  );
}
