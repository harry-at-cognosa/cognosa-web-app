import { createTableStore } from "../../tables/TableStoreFactory";
import UniversalTable from "../../tables/UniversalTable";

const useTableSuManageUsersStore = createTableStore({
  title: "SU Manage Users",
  name: "su_manage_users",
  endpoint: "/su/manage_users",
});

export default function TableSuManageUsers() {
  return <UniversalTable useStore={useTableSuManageUsersStore} />;
}
