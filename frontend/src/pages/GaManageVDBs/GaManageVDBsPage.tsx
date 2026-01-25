import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableGaManageVDBs from "./GaTableManageVDBs";

export default function GaManageVDBsPage() {
  useTopNavBarTitle("Manage VDBs");
  return (
    <div className="container-fluid my-4">
      <TableGaManageVDBs />
    </div>
  );
}
