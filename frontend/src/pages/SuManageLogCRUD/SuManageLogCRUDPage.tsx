import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableSuManageLogCRUD from "./SuTableManageLogCRUD";

export default function SuManageLogCRUDPage() {
  useTopNavBarTitle("Manage Log CRUD");
  return (
    <div className="container-fluid my-4">
      <TableSuManageLogCRUD />
    </div>
  );
}
