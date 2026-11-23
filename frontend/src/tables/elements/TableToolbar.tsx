import type { createTableStore } from "../TableStoreFactory";
import CreateRowButton from "./CreateRowButton";
import ExportButton from "./ExportButton";
import PaginationControls from "./PaginationControls/PaginationControls";
import TableReloadButton from "./TableReloadButton";
import TableTitle from "./TableTitle";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

// The bar above the column headers: Add, title, reload, paging, limit, export.
export default function TableToolbar({ useStore }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-x-2.5 gap-y-2 px-4 py-3.5">
      <CreateRowButton useStore={useStore} />
      <TableTitle useStore={useStore} />
      <TableReloadButton useStore={useStore} />
      <PaginationControls useStore={useStore} />
      <span className="flex-1" />
      <ExportButton useStore={useStore} />
    </div>
  );
}
