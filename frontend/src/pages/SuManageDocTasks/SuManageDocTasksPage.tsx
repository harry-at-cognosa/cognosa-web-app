import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import TableSuManageDocTasks from "./SuTableManageDocTasks";

export default function SuManageDocTasksPage() {
  useTopNavBarTitle("Manage Doc Tasks");
  return (
    <TablePage>
      <TableSuManageDocTasks />
    </TablePage>
  );
}
