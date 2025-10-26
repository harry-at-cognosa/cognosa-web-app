import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableGaManageUsers from "./TableGaManageUsers";

export default function GaManageUsersPage() {
  useTopNavBarTitle("Manage Users");
  return (
    <div className="container-fluid my-4">
      <TableGaManageUsers />
    </div>
  );
}
