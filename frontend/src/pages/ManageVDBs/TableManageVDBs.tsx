import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableManageVDBsStore = createTableStore({
  title: "Group VDBs",
  name: "manage_vdbs",
  endpoint: "/manage_vdbs",
});

export default function TableManageVDBs() {
  return <UniversalTable useStore={useTableManageVDBsStore} />;
}
