import UniversalTable from "../../../tables/UniversalTable";
import { createTableStore } from "../../../tables/TableStoreFactory";

const useTableManageUsersStore = createTableStore({
  name: "manage_users",
  endpoint: "/manage_users",
});

export default function TableManageUsers() {
  return <UniversalTable useStore={useTableManageUsersStore} />;
}
