import { Button } from "react-bootstrap";
import type { createTableStore } from "../TableStoreFactory";
import { ArrowRepeat } from "react-bootstrap-icons";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableReloadButton({ useStore }: Props) {
  const tableStore = useStore();
  return (
    <Button
      type="button"
      variant=""
      className="mx-3 fw-bold p-0 btn-tc-200-300"
      onClick={() => tableStore.setNeedReload(true)}
    >
      <ArrowRepeat size="1.75rem" className="fw-bold"></ArrowRepeat>
    </Button>
  );
}
