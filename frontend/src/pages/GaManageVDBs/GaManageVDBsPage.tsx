import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import TableGaManageVDBs from "./GaTableManageVDBs";

export default function GaManageVDBsPage() {
  useTopNavBarTitle("Manage Collections");
  return (
    <TablePage>
      <TableGaManageVDBs />
    </TablePage>
  );
}
