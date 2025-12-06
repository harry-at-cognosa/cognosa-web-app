import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableGaManageDocTasksStore = createTableStore({
  title: "Manage Queries",
  name: "ga_manage_doc_tasks",
  endpoint: "/ga/manage_doc_tasks",
  order_by: "doc_task_id",
  order_dir: "desc",
});

export default function TableGaManageDocTasks() {
  return <UniversalTable useStore={useTableGaManageDocTasksStore} />;
}
