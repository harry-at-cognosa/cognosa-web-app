import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import ResizableTableWidth from "../../tables/elements/ResizableTableWidth";
import TableManageContexts from "./TableManageContexts";

export default function ManageContextsPage() {
  useTopNavBarTitle("Manage Contexts");
  return (
    <ResizableTableWidth table="manage_contexts">
      <TableManageContexts />
    </ResizableTableWidth>
  );
}
