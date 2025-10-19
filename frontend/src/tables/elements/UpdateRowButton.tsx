import { Button } from "react-bootstrap";
import type { createTableStore, TableRow } from "../TableStoreFactory";

interface Props {
  row: TableRow;
  useStore: ReturnType<typeof createTableStore>;
}

export default function UpdateRowButton({ row, useStore }: Props) {
  const { data, setShowCreateOrUpdateDialog } = useStore();
  if (!data?.table_options?.update__ask_columns.length) return null;

  return (
    <Button
      type="button"
      variant="primary"
      className="fw-bold"
      onClick={() => setShowCreateOrUpdateDialog("update", { ...row })}
    >
      Edit
    </Button>
  );
}
