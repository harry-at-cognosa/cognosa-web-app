import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableSuManageDocTasks from "./SuTableManageDocTasks";

export default function SuManageDocTasksPage() {
  useTopNavBarTitle("Manage Doc Tasks");
  return (
    <div className="container-fluid my-4">
      <TableSuManageDocTasks />
    </div>
  );
}
