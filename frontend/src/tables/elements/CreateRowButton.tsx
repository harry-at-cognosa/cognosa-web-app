import { Button } from "react-bootstrap";
import type { createTableStore, TableRow } from "../TableStoreFactory";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";
import { useState } from "react";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function CreateRowButton({ useStore }: Props) {
  const [isHovered, setIsHovered] = useState(false);
  const { data, setShowCreateOrUpdateDialog } = useStore();
  const { color } = useWebAppOptionsStore();
  if (!data?.table_options?.create__ask_columns.length) return null;
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
      className="me-3 fw-bold px-4"
      style={{ backgroundColor: isHovered ? color.c400 : color.c300 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => setShowCreateOrUpdateDialog("create", makeInitialDict())}
    >
      + Add
    </Button>
  );
}
