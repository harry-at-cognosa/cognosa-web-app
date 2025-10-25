import { useEffect } from "react";
import { Table, Spinner, Alert, Button } from "react-bootstrap";
import type { createTableStore } from "./TableStoreFactory";
import ViewCellElement from "./elements/ViewCellElement";
import DeleteDialog from "./elements/DeleteDialog";
import EditDialog from "./elements/EditDialog";
import UpdateRowButton from "./elements/UpdateRowButton";
import TableHeader from "./elements/TableHeader";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function UniversalTable({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;

  useEffect(() => {
    if (!tableStore.needReload) return;
    tableStore.queryTable();
  }, [tableStore.needReload]);
  useEffect(() => tableStore.setNeedReload(true), []);

  if (tableStore.busy) return <Spinner animation="border" />;
  if (!data) return <p>No data</p>;

  return (
    <>
      {tableStore.error ? (
        <Alert variant="danger">{tableStore.error}</Alert>
      ) : null}
      <Table bordered hover responsive>
        <TableHeader useStore={useStore}></TableHeader>
        <tbody>
          {data.rows.map((row) => (
            <tr
              key={row[data.table_options.pk]?.toString()}
              style={{ textAlign: "center", verticalAlign: "middle" }}
            >
              {/* edit button cell */}
              {data.table_options.update__ask_columns.length ? (
                <td
                  key={row[data.table_options.pk]?.toString() + "__edit"}
                  style={{ width: "1px" }}
                >
                  <UpdateRowButton
                    row={row}
                    useStore={useStore}
                  ></UpdateRowButton>
                </td>
              ) : null}
              {/* visible columns */}
              {tableStore.data?.table_options?.read__visible_columns.map(
                (col) => (
                  <ViewCellElement
                    data={data}
                    row={row}
                    col={col}
                    key={
                      row[data.table_options.pk]?.toString() + "__vce__" + col
                    }
                  ></ViewCellElement>
                )
              )}
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
      </Table>
      <EditDialog useStore={useStore}></EditDialog>
      <DeleteDialog useStore={useStore}></DeleteDialog>
    </>
  );
}
