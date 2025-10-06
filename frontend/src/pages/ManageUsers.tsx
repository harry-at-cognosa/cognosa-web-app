import { useTopNavBarTitle } from "../hooks/useTopNavBarTitle";
import TableManageUsers from "./elements/ManageUsers/TableManageUsers";

export default function ManageUsers() {
  useTopNavBarTitle("Manage Users");
  return (
    <div className="container-fluid my-4">
      <h2>Manage Users</h2>
      <TableManageUsers />
    </div>
  );
}
