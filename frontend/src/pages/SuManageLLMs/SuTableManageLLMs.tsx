import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableSuManageLLMsStore = createTableStore({
  title: "Group LLMs",
  name: "su_manage_llms",
  endpoint: "/su/manage_llms",
});

export default function TableSuManageLLMs() {
  return <UniversalTable useStore={useTableSuManageLLMsStore} />;
}
