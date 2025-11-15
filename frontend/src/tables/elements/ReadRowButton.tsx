import { Button } from "react-bootstrap";
import type { createTableStore, TableRow } from "../TableStoreFactory";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";
import { useState } from "react";

interface Props {
  row: TableRow;
  useStore: ReturnType<typeof createTableStore>;
}

export default function ReadRowButton({ row, useStore }: Props) {
  const [isHovered, setIsHovered] = useState(false);
  const { setReadRow } = useStore();
  const { color } = useWebAppOptionsStore();

  return (
    <Button
      type="button"
      variant=""
      className="fw-bold"
      onClick={() => setReadRow({ ...row })}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        color: "black",
        backgroundColor: isHovered ? color.c400 : color.c300,
      }}
    >
      View
    </Button>
  );
}
