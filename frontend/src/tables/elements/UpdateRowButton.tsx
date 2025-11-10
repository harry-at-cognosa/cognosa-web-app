import { Button } from "react-bootstrap";
import type { createTableStore, TableRow } from "../TableStoreFactory";

interface Props {
  row: TableRow;
  useStore: ReturnType<typeof createTableStore>;
}

export default function UpdateRowButton({ row, useStore }: Props) {
  const { data, setShowCreateOrUpdateDialog } = useStore();
  if (!data?.table_options) return;
  if (!data.table_options.update__ask_columns.length) return null;
  const pk_value_str = (row[data.table_options.pk] || -1).toString();

  return (
    <Button
      type="button"
      id={`btn_update__${data.name}__${pk_value_str}`}
      variant="primary"
      className="fw-bold"
      onClick={() => setShowCreateOrUpdateDialog("update", { ...row })}
    >
      Edit
    </Button>
  );
}
