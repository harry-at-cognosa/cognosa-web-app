import { Button } from "react-bootstrap";
import type { createTableStore, TableRow } from "../TableStoreFactory";

interface Props {
  row: TableRow;
  useStore: ReturnType<typeof createTableStore>;
}

export default function ReadRowButton({ row, useStore }: Props) {
  const { setReadRow } = useStore();

  return (
    <Button
      type="button"
      variant=""
      className="fw-bold btn-tc-300-400"
      onClick={() => setReadRow({ ...row })}
    >
      View
    </Button>
  );
}
