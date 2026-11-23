import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import TableSuManageApiSettings from "./SuTableManageApiSettings";

export default function SuManageApiSettingsPage() {
  useTopNavBarTitle("Manage Api Settings");
  return (
    <TablePage>
      <TableSuManageApiSettings />
    </TablePage>
  );
}
