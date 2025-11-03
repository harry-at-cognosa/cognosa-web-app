import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableSuManageLogCRUDStore = createTableStore({
  title: "Manage Log CRUD",
  name: "su_manage_log_crud",
  endpoint: "/su/manage_log_crud",
});

export default function TableSuManageLogCRUD() {
  return <UniversalTable useStore={useTableSuManageLogCRUDStore} />;
}
