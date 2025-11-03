import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableSuManageDocTasksStore = createTableStore({
  title: "Manage Doc Tasks",
  name: "su_manage_doc_tasks",
  endpoint: "/su/manage_doc_tasks",
});

export default function TableSuManageDocTasks() {
  return <UniversalTable useStore={useTableSuManageDocTasksStore} />;
}
