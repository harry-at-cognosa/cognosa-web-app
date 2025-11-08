import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";
import type { createTableStore } from "../TableStoreFactory";
import CreateRowButton from "./CreateRowButton";
import HeaderColumnsRow from "./HeaderColumnsRow";
import PaginationControls from "./PaginationControls";
import TableReloadButton from "./TableReloadButton";
import TableTitle from "./TableTitle";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableHeader({ useStore }: Props) {
  const { color } = useWebAppOptionsStore();
  return (
    <thead>
      <tr>
        <th colSpan={100} style={{ backgroundColor: color.c200 }}>
          <div className="d-flex">
            <CreateRowButton useStore={useStore}></CreateRowButton>
            <TableTitle useStore={useStore}></TableTitle>
            <TableReloadButton useStore={useStore}></TableReloadButton>
            <PaginationControls useStore={useStore}></PaginationControls>
          </div>
        </th>
      </tr>
      <HeaderColumnsRow useStore={useStore}></HeaderColumnsRow>
    </thead>
  );
}
