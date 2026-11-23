import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import TableGaManageUsers from "./TableGaManageUsers";

export default function GaManageUsersPage() {
  useTopNavBarTitle("Manage Users");
  return (
    <TablePage>
      <TableGaManageUsers />
    </TablePage>
  );
}
