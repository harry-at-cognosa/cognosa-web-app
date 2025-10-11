import { Button, Modal, Table } from "react-bootstrap";
import type { createTableStore } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";
import ViewCellElement from "./ViewCellElement";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function AskDelete({ useStore }: Props) {
  const tableStore = useStore();
  const { data, askDelete } = tableStore;
  if (!data) return null;
  if (!askDelete) return null;
  const { delete_ask_columns } = data.table_options;
  const handleClose = () => tableStore.setAskDelete(null);
  return (
    <Modal show={Boolean(askDelete)} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Confirm delete:</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {delete_ask_columns.map((col) => (
          <Table bordered key={col + "__col_table"}>
            <tbody>
              <tr key={col + "__col_name"}>
                <th>
                  <ColumnDisplayName data={data} col={col}></ColumnDisplayName>:
                </th>
              </tr>
              <tr key={col + "__col_value"}>
                <td>
                  <ViewCellElement
                    data={data}
                    row={askDelete}
                    col={col}
                  ></ViewCellElement>
                </td>
              </tr>
            </tbody>
          </Table>
        ))}
      </Modal.Body>
      <Modal.Footer>
        <Button
          variant="danger"
          onClick={tableStore.deleteRow}
          disabled={tableStore.deleting}
        >
          Delete
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
