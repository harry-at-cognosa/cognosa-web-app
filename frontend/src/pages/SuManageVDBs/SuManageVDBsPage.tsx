import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import TableSuManageVDBs from "./SuTableManageVDBs";

export default function SuManageVDBsPage() {
  useTopNavBarTitle("Manage VDBs");
  return (
    <TablePage>
      <TableSuManageVDBs />
    </TablePage>
  );
}
