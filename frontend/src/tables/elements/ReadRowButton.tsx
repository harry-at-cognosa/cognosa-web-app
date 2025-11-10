import { Button } from "react-bootstrap";
import type { createTableStore, TableRow } from "../TableStoreFactory";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";

interface Props {
  row: TableRow;
  useStore: ReturnType<typeof createTableStore>;
}

export default function ReadRowButton({ row, useStore }: Props) {
  const { setReadRow } = useStore();
  const { color } = useWebAppOptionsStore();

  return (
    <Button
      type="button"
      variant=""
      className="fw-bold"
      onClick={() => setReadRow({ ...row })}
      style={{ color: "black", backgroundColor: color.c300 }}
    >
      View
    </Button>
  );
}
