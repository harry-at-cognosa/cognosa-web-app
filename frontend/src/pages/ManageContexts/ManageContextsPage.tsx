import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import { PageHead } from "@/components/Shell";
import ResizableTableWidth from "../../tables/elements/ResizableTableWidth";
import TableManageContexts from "./TableManageContexts";

export default function ManageContextsPage() {
  useTopNavBarTitle("Manage Contexts");
  return (
    // the heading sits inside the resizable wrapper so it stays aligned with the table
    <ResizableTableWidth table="manage_contexts">
      <PageHead className="mb-3" />
      <TableManageContexts />
    </ResizableTableWidth>
  );
}
