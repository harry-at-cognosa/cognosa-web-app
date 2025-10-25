import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableSuManageLLMs from "./SuTableManageLLMs";

export default function SuManageLLMsPage() {
  useTopNavBarTitle("Manage LLMs");
  return (
    <div className="container-fluid my-4">
      <TableSuManageLLMs />
    </div>
  );
}
