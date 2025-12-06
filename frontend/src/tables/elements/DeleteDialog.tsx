import { Button, Modal, Table } from "react-bootstrap";
import type { createTableStore } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";
import ViewCellElement from "./ViewCellElement";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function DeleteDialog({ useStore }: Props) {
  const tableStore = useStore();
  const { data, deleteRow, setDeleteRow } = tableStore;
  if (!data) return null;
  if (!deleteRow) return null;
  const { delete__ask_columns } = data.table_options;
  const handleClose = () => setDeleteRow(null);
  return (
    <Modal show={Boolean(deleteRow)} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Confirm delete:</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {delete__ask_columns.map((col) => (
          <Table bordered key={col + "__col_table"}>
            <tbody>
              <tr key={col + "__col_name"}>
                <th className="bg-tc-100">
                  <ColumnDisplayName
                    nameType="dialog"
                    data={data}
                    col={col}
                  ></ColumnDisplayName>
                </th>
              </tr>
              <tr key={col + "__col_value"}>
                <ViewCellElement
                  useStore={useStore}
                  row={deleteRow}
                  col={col}
                ></ViewCellElement>
              </tr>
            </tbody>
          </Table>
        ))}
      </Modal.Body>
      <Modal.Footer>
        <Button
          variant="danger"
          onClick={tableStore.queryDeleteRow}
          disabled={tableStore.busy != ""}
          className="fw-bold"
        >
          Delete
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
