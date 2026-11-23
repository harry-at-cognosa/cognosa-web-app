import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import TableSuManageUsers from "./TableSuManageUsers";

export default function SuManageUsersPage() {
  useTopNavBarTitle("SU Manage Users");
  return (
    <TablePage>
      <TableSuManageUsers />
    </TablePage>
  );
}
