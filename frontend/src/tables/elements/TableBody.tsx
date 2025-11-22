import { Button, Spinner } from "react-bootstrap";
import ViewCellElement from "./ViewCellElement";
import UpdateRowButton from "./UpdateRowButton";
import ReadRowButton from "./ReadRowButton";
import type { createTableStore } from "../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableBody({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;
  if (!data) return null;
  if (tableStore.busy === "read") return <Spinner />;
  if (!data) return <p>No data</p>;
  return (
    <tbody>
      {data.rows.map((row) => (
        <tr
          key={row[data.table_options.pk]?.toString()}
          style={{ textAlign: "center", verticalAlign: "middle" }}
        >
          {/* view/edit button cell */}
          <td
            key={row[data.table_options.pk]?.toString() + "__edit"}
            style={{ width: "1px" }}
          >
            {data.table_options.update__ask_columns.length ? (
              <UpdateRowButton row={row} useStore={useStore}></UpdateRowButton>
            ) : (
              <ReadRowButton row={row} useStore={useStore}></ReadRowButton>
            )}
          </td>
          {/* visible columns */}
          {tableStore.data?.table_options?.read__visible_columns.map((col) => (
            <ViewCellElement
              useStore={useStore}
              row={row}
              col={col}
              key={row[data.table_options.pk]?.toString() + "__vce__" + col}
            ></ViewCellElement>
          ))}
          {/* delete button cell */}
          {data.table_options.delete__ask_columns.length ? (
            <td
              key={row[data.table_options.pk]?.toString() + "__delete"}
              style={{ width: "1px" }}
            >
              <Button
                type="button"
                variant="secondary"
                onClick={() => tableStore.setDeleteRow(row)}
              >
                X
              </Button>
            </td>
          ) : null}
        </tr>
      ))}
    </tbody>
  );
}
