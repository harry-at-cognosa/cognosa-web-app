import type { createTableStore } from "../TableStoreFactory";
import CreateRowButton from "./CreateRowButton";
import ExportButton from "./ExportButton";
import HeaderColumnsRow from "./HeaderColumnsRow";
import PaginationControls from "./PaginationControls/PaginationControls";
import TableReloadButton from "./TableReloadButton";
import TableTitle from "./TableTitle";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableHeader({ useStore }: Props) {
  return (
    <thead>
      <tr>
        <th colSpan={100} className="bg-tc-200">
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
