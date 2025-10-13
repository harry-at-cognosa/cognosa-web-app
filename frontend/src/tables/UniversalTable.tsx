import { useEffect } from "react";
import { Table, Spinner, Alert, Button } from "react-bootstrap";
import type { createTableStore } from "./TableStoreFactory";
import ViewCellElement from "./elements/ViewCellElement";
import DeleteDialog from "./elements/DeleteDialog";
import HeaderColumnsRow from "./elements/HeaderColumnsRow";
import TableTitle from "./elements/TableTitle";
import CreateRowButton from "./elements/CreateRowButton";
import EditDialog from "./elements/EditDialog";
import UpdateRowButton from "./elements/UpdateRowButton";

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
        <thead>
          <tr>
            <th colSpan={100}>
              <div className="d-flex">
                <CreateRowButton useStore={useStore}></CreateRowButton>
                <TableTitle useStore={useStore}></TableTitle>
              </div>
            </th>
          </tr>
          <HeaderColumnsRow useStore={useStore}></HeaderColumnsRow>
        </thead>
        <tbody>
          {data.rows.map((row) => (
            <tr
              key={row[data.table_options.pk]?.toString()}
              style={{ textAlign: "center", verticalAlign: "middle" }}
            >
              {/* edit button cell */}
              <td>
                <UpdateRowButton
                  row={row}
                  useStore={useStore}
                ></UpdateRowButton>
              </td>
              {/* visible columns */}
              {tableStore.visible_columns.map((col) => (
                <td key={col}>
                  <ViewCellElement
                    data={data}
                    row={row}
                    col={col}
                  ></ViewCellElement>
                </td>
              ))}
              {/* delete button cell */}
              {data.table_options.delete__allow ? (
                <td>
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
