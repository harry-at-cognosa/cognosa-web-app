import { Button, Modal, Table } from "react-bootstrap";
import type { createTableStore } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";
import EditCellElement from "./EditCellElement";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function EditDialog({ useStore }: Props) {
  const tableStore = useStore();
  const { data, showCreateOrUpdateDialog } = tableStore;
  if (!data) return null;
  if (!showCreateOrUpdateDialog) return null;
  const isCreate = showCreateOrUpdateDialog === "create";
  const { create__ask_columns, update__ask_columns } = data.table_options;
  const ask_columns = isCreate ? create__ask_columns : update__ask_columns;
  const handleClose = () => tableStore.setShowCreateOrUpdateDialog("", null);

  return (
    <Modal
      size="xl"
      show={Boolean(showCreateOrUpdateDialog)}
      onHide={handleClose}
    >
      <Modal.Header closeButton>
        <Modal.Title>{isCreate ? "Add new:" : "Edit:"}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {ask_columns.map((col) => (
          <div key={"div__" + col}>
            <div className="fw-bold ms-2" key={"div_label__" + col}>
              <ColumnDisplayName data={data} col={col}></ColumnDisplayName>
            </div>
            <div className="mb-2" key={"div_value__" + col}>
              <EditCellElement useStore={useStore} col={col}></EditCellElement>
            </div>
          </div>
        ))}
      </Modal.Body>
      <Modal.Footer>
        <Button
          variant={isCreate ? "warning" : "primary"}
          onClick={tableStore.queryEditRow}
          disabled={tableStore.busy != ""}
        >
          Save
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
