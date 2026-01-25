import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableGaManageVDBsStore = createTableStore({
  title: "Group VDBs",
  name: "ga_manage_vdbs",
  endpoint: "/groupadmin/manage_vdbs",
});

export default function TableGaManageVDBs() {
  return <UniversalTable useStore={useTableGaManageVDBsStore} />;
}
