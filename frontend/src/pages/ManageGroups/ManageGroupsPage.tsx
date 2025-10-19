import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableManageGroups from "./TableManageGroups";

export default function ManageGroupsPage() {
  useTopNavBarTitle("Manage Groups");
  return (
    <div className="container my-4">
      <TableManageGroups />
    </div>
  );
}
