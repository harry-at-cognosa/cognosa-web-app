import UniversalTable from "../../tables/UniversalTable";
import { createTableStore } from "../../tables/TableStoreFactory";

const useTableManageLLMsStore = createTableStore({
  title: "Group LLMs",
  name: "manage_llms",
  endpoint: "/manage_llms",
});

export default function TableManageLLMs() {
  return <UniversalTable useStore={useTableManageLLMsStore} />;
}
