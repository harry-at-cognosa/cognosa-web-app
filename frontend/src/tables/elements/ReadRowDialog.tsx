import { Button, Modal, Table } from "react-bootstrap";
import type { createTableStore } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";
import ViewCellElement from "./ViewCellElement";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";
import ExportButton from "./ExportButton";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function ReadRowDialog({ useStore }: Props) {
  const { color } = useWebAppOptionsStore();
  const tableStore = useStore();
  const { data, readRow, setReadRow } = tableStore;
  if (!data) return null;
  if (!readRow) return null;
  const { read__visible_columns } = data.table_options;
  const handleClose = () => setReadRow(null);
  return (
    <Modal show={Boolean(readRow)} onHide={handleClose} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Row values:</Modal.Title>
        <div className="mx-auto mt-1" style={{ fontSize: "large" }}>
          <ExportButton useStore={useStore} row={readRow} />
        </div>
      </Modal.Header>
      <Modal.Body>
        {read__visible_columns.map((col) => (
          <Table bordered key={col + "__col_table"}>
            <tbody>
              <tr key={col + "__col_name"}>
                <th>
                  <ColumnDisplayName data={data} col={col}></ColumnDisplayName>:
                </th>
              </tr>
              <tr key={col + "__col_value"}>
                <ViewCellElement
                  useStore={useStore}
                  row={readRow}
                  col={col}
                ></ViewCellElement>
              </tr>
            </tbody>
          </Table>
        ))}
      </Modal.Body>
      <Modal.Footer>
        <Button
          variant=""
          onClick={handleClose}
          className="fw-bold"
          style={{ backgroundColor: color.c300 }}
        >
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
