import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";

const useTableSuManageApiSettingsStore = createTableStore({
  title: "Manage Api Settings",
  name: "su_manage_api_settings",
  endpoint: "/su/manage_api_settings",
  afterEdit: async (get) => {
    const editRow = get().editRow;
    if (editRow?.name === "webapp_main_color") {
      useWebAppOptionsStore.getState().setNeedReload(true);
    }
  },
});

export default function TableSuManageApiSettings() {
  return <UniversalTable useStore={useTableSuManageApiSettingsStore} />;
}
