import { Button } from "react-bootstrap";
import type { createTableStore } from "../TableStoreFactory";
import { ArrowRepeat } from "react-bootstrap-icons";
import { useState } from "react";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableReloadButton({ useStore }: Props) {
  const [isHovered, setIsHovered] = useState(false);
  const tableStore = useStore();
  const { color } = useWebAppOptionsStore();
  return (
    <Button
      type="button"
      variant=""
      className="mx-3 fw-bold p-0"
      style={{ backgroundColor: isHovered ? color.c300 : "" }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => tableStore.setNeedReload(true)}
    >
      <ArrowRepeat size="1.75rem" className="fw-bold"></ArrowRepeat>
    </Button>
  );
}
