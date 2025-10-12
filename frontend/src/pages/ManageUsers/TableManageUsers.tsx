import { createTableStore } from "../../tables/TableStoreFactory";
import UniversalTable from "../../tables/UniversalTable";

const useTableManageUsersStore = createTableStore({
  name: "manage_users",
  endpoint: "/manage_users",
});

export default function TableManageUsers() {
  return <UniversalTable useStore={useTableManageUsersStore} />;
}
