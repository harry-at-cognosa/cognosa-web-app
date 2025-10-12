import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableManageUsers from "./TableManageUsers";

export default function ManageUsersPage() {
  useTopNavBarTitle("Manage Users");
  return (
    <div className="container-fluid my-4">
      <h2>Manage Users</h2>
      <TableManageUsers />
    </div>
  );
}
