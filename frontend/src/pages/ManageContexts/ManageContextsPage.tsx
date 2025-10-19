import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableManageContexts from "./TableManageContexts";

export default function ManageContextsPage() {
  useTopNavBarTitle("Manage Contexts");
  return (
    <div className="container my-4">
      <TableManageContexts />
    </div>
  );
}
