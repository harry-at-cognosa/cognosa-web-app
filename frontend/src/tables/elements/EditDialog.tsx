import { Button, Modal } from "react-bootstrap";
import type { createTableStore } from "../TableStoreFactory";
import EditCellElement from "./EditCellElement";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";
import ExportButton from "./ExportButton";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

function EditMsg({ msg, key_ }: { msg: string; key_: string }) {
  const text_lines = msg
    .trim()
    .split("\n")
    .map((x) => x.trim());
  return (
    <div className="px-3 py-0 mt-1" key={key_}>
      {text_lines.map((line, i) => (
        <div key={key_ + "__line_" + i} style={{ fontSize: "smaller" }}>
          {line}
        </div>
      ))}
    </div>
  );
}

export default function EditDialog({ useStore }: Props) {
  const { color } = useWebAppOptionsStore();
  const tableStore = useStore();
  const { data, showCreateOrUpdateDialog } = tableStore;
  if (!data) return null;
  if (!showCreateOrUpdateDialog) return null;
  const isCreate = showCreateOrUpdateDialog === "create";
  const { create__ask_columns, update__ask_columns } = data.table_options;
  const ask_columns = isCreate ? create__ask_columns : update__ask_columns;
  const handleClose = () => tableStore.setShowCreateOrUpdateDialog("", null);
  const haveErrors = !!Object.keys(tableStore.editRowErrorMsg).length;
  return (
    <Modal
      size="xl"
      show={Boolean(showCreateOrUpdateDialog)}
      onHide={handleClose}
      style={{ zIndex: 1050 }}
    >
      <Modal.Header closeButton>
        <Modal.Title>
          <span>{isCreate ? "Add new:" : "Edit:"}</span>
          {haveErrors ? (
            <span className="fw-bold ms-5" style={{ color: "red" }}>
              Found errors!
            </span>
          ) : null}
          {tableStore.editRow ? (
            <div className="mx-auto mt-1" style={{ fontSize: "large" }}>
              <ExportButton useStore={useStore} row={tableStore.editRow} />
            </div>
          ) : null}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {ask_columns.map((col) => (
          <div
            key={"div__" + col}
            className="p-1 mb-4"
            style={{ borderRadius: "5px", backgroundColor: color.c100 }}
          >
            <div className="fw-bold mt-0 ms-2" key={"div_label__" + col}>
              <span>
                {data.columns[col].display || col}
                {data.columns[col].cu_required ? (
                  <span style={{ color: "red" }}>*</span>
                ) : null}
              </span>
              {tableStore.editRowErrorMsg[col] ? (
                <span
                  className="ms-3"
                  key={"div_error_msg__" + col}
                  style={{ color: "red" }}
                >
                  {tableStore.editRowErrorMsg[col]}
                </span>
              ) : null}
            </div>
            <div className="mb-0" key={"div_value__" + col}>
              <EditCellElement useStore={useStore} col={col}></EditCellElement>
            </div>
            {data.columns[col].cu_edit_msg ? (
              <EditMsg
                msg={data.columns[col].cu_edit_msg}
                key_={"div_desc__" + col}
              />
            ) : null}
          </div>
        ))}
      </Modal.Body>
      <Modal.Footer>
        <Button
          className="mx-auto fw-bold"
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
