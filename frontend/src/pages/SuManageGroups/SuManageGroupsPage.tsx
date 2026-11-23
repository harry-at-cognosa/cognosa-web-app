import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import SuTableManageGroups from "./TableSuManageGroups";

export default function SuManageGroupsPage() {
  useTopNavBarTitle("Manage Groups");
  return (
    <TablePage>
      <SuTableManageGroups />
    </TablePage>
  );
}
