import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import TableGaManageDocTasks from "./GaTableManageDocTasks";

export default function GaManageDocTasksPage() {
  useTopNavBarTitle("Manage Queries");
  return (
    <TablePage>
      <TableGaManageDocTasks />
    </TablePage>
  );
}
