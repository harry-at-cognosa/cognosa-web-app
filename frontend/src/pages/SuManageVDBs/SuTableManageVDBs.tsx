import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableSuManageVDBsStore = createTableStore({
  title: "Group VDBs",
  name: "su_manage_vdbs",
  endpoint: "/su/manage_vdbs",
});

export default function TableSuManageVDBs() {
  return <UniversalTable useStore={useTableSuManageVDBsStore} />;
}
