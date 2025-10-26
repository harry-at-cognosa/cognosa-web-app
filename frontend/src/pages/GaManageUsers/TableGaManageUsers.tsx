import { createTableStore } from "../../tables/TableStoreFactory";
import UniversalTable from "../../tables/UniversalTable";

const useTableGaManageUsersStore = createTableStore({
  title: "Manage Users",
  name: "ga_manage_users",
  endpoint: "/groupadmin/manage_users",
});

export default function TableGaManageUsers() {
  return <UniversalTable useStore={useTableGaManageUsersStore} />;
}
