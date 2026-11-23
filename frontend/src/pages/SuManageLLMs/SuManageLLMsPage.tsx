import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TablePage from "../../tables/elements/TablePage";
import TableSuManageLLMs from "./SuTableManageLLMs";

export default function SuManageLLMsPage() {
  useTopNavBarTitle("Manage LLMs");
  return (
    <TablePage>
      <TableSuManageLLMs />
    </TablePage>
  );
}
