import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableGaManageDocTasks from "./GaTableManageDocTasks";

export default function GaManageDocTasksPage() {
  useTopNavBarTitle("Manage Queries");
  return (
    <div className="container-fluid my-4">
      <TableGaManageDocTasks />
    </div>
  );
}
