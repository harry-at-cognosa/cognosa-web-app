import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableSuManageApiSettings from "./SuTableManageApiSettings";

export default function SuManageApiSettingsPage() {
  useTopNavBarTitle("Manage Api Settings");
  return (
    <div className="container my-4">
      <TableSuManageApiSettings />
    </div>
  );
}
