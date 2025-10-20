import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableManageVDBs from "./TableManageVDBs";

export default function ManageVDBsPage() {
  useTopNavBarTitle("Manage VDBs");
  return (
    <div className="container-fluid my-4">
      <TableManageVDBs />
    </div>
  );
}
