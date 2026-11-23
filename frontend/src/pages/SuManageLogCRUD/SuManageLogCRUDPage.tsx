import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import TableSuManageLogCRUD from "./SuTableManageLogCRUD";

export default function SuManageLogCRUDPage() {
  useTopNavBarTitle("Manage Log CRUD");
  return (
    <TablePage>
      <TableSuManageLogCRUD />
    </TablePage>
  );
}
