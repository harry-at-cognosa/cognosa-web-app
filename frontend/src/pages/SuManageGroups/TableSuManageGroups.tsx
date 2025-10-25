import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableSuManageGroupsStore = createTableStore({
  title: "Manage Groups",
  name: "su_manage_groups",
  endpoint: "/su/manage_groups",
});

export default function SuTableManageGroups() {
  return <UniversalTable useStore={useTableSuManageGroupsStore} />;
}
