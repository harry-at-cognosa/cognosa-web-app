import { Button } from "react-bootstrap";
import type { createTableStore, TableRow } from "../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function CreateRowButton({ useStore }: Props) {
  const { data, setShowCreateOrUpdateDialog } = useStore();
  if (!data?.table_options?.create__allow) return null;
  function makeInitialDict() {
    const row: TableRow = {};
    data?.table_options.create__ask_columns.map((col) => {
      row[col] = data?.columns[col].default;
    });
    return row;
  }

  return (
    <Button
      type="button"
      variant="warning"
      className="me-3 fw-bold"
      onClick={() => setShowCreateOrUpdateDialog("create", makeInitialDict())}
    >
      + Add
    </Button>
  );
}
