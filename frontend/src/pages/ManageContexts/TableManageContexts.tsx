import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableManageContextsStore = createTableStore({
  title: "Group Contexts",
  name: "manage_contexts",
  endpoint: "/manage_contexts",
});

export default function TableManageContexts() {
  return <UniversalTable useStore={useTableManageContextsStore} />;
}
