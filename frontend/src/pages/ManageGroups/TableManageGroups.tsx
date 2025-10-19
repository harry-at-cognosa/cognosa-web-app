import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableManageGroupsStore = createTableStore({
  title: "Manage Groups",
  name: "manage_groups",
  endpoint: "/manage_groups",
});

export default function TableManageGroups() {
  return <UniversalTable useStore={useTableManageGroupsStore} />;
}
