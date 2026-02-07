import { Button } from "react-bootstrap";
import ViewCellElement from "./ViewCellElement";
import UpdateRowButton from "./UpdateRowButton";
import ReadRowButton from "./ReadRowButton";
import type { createTableStore } from "../TableStoreFactory";
import { BusyCell } from "../CellRenders/BusyCell";
import { useLayoutEffect, useRef } from "react";
import { fixTextareaHeights } from "../functions/fixTextareaHeights";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableBody({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;
  const tbodyRef = useRef<HTMLTableSectionElement | null>(null);
  if (!data) return null;
  const isBusy = tableStore.busy === "read";
  useLayoutEffect(() => {
    if (!tbodyRef.current) return;
    fixTextareaHeights(tbodyRef.current);
  }, [data.rows, data.table_options.read__visible_columns, tableStore.busy]);
  return (
    <tbody ref={tbodyRef}>
      {data.rows.map((row) => (
        <tr
          key={row[data.table_options.pk]?.toString()}
          style={{ textAlign: "center", verticalAlign: "middle" }}
        >
          {/* view/edit button cell */}
          <td
            key={row[data.table_options.pk]?.toString() + "__edit"}
            className="position-relative"
            style={{ width: "1px" }}
          >
            <div className="content-wrapper">
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
          </td>
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
            <td
              key={row[data.table_options.pk]?.toString() + "__delete"}
              className="position-relative"
              style={{ width: "1px" }}
            >
              <div className="content-wrapper">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => tableStore.setDeleteRow(row)}
                >
                  X
                </Button>
              </div>
              <BusyCell isBusy={isBusy} />
            </td>
          ) : null}
        </tr>
      ))}
    </tbody>
  );
}
