import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableSuManageVDBs from "./SuTableManageVDBs";

export default function SuManageVDBsPage() {
  useTopNavBarTitle("Manage VDBs");
  return (
    <div className="container-fluid my-4">
      <TableSuManageVDBs />
    </div>
  );
}
