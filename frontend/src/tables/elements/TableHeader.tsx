import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";
import type { createTableStore } from "../TableStoreFactory";
import CreateRowButton from "./CreateRowButton";
import ExportButton from "./ExportButton";
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
            <CreateRowButton useStore={useStore} />
            <TableTitle useStore={useStore} />
            <TableReloadButton useStore={useStore} />
            <PaginationControls useStore={useStore} />
            <ExportButton useStore={useStore} />
          </div>
        </th>
      </tr>
      <HeaderColumnsRow useStore={useStore} />
    </thead>
  );
}
