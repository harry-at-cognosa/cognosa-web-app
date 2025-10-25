import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import SuTableManageGroups from "./TableSuManageGroups";

export default function SuManageGroupsPage() {
  useTopNavBarTitle("Manage Groups");
  return (
    <div className="container my-4">
      <SuTableManageGroups />
    </div>
  );
}
