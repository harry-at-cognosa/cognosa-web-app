import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableSuManageUsers from "./TableSuManageUsers";

export default function SuManageUsersPage() {
  useTopNavBarTitle("SU Manage Users");
  return (
    <div className="container-fluid my-4">
      <TableSuManageUsers />
    </div>
  );
}
