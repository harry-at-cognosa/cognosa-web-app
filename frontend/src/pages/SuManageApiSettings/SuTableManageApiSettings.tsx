import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";
import { useDocTaskOptionsStore } from "../QueryDocuments/stores/useDocTaskOptionsStore";
import { useDocTasksGVDBsCfgStore } from "../../components/GVDBsCfg/stores";

const useTableSuManageApiSettingsStore = createTableStore({
  title: "Manage Api Settings",
  name: "su_manage_api_settings",
  endpoint: "/su/manage_api_settings",
  afterEdit: async (get) => {
    const editRow = get().editRow;
    const name = editRow?.name?.toString();
    if (name === "webapp_main_color") {
      useWebAppOptionsStore.getState().setNeedReload(true);
    }
    if (name === "gvdbs_cfg_json") {
      useDocTaskOptionsStore.getState().setNeedReload(true);
      useDocTasksGVDBsCfgStore.getState().setDefaultValues();
    }
  },
});

export default function TableSuManageApiSettings() {
  return <UniversalTable useStore={useTableSuManageApiSettingsStore} />;
}
