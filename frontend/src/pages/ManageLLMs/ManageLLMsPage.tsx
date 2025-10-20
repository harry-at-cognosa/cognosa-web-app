import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableManageLLMs from "./TableManageLLMs";

export default function ManageLLMsPage() {
  useTopNavBarTitle("Manage LLMs");
  return (
    <div className="container-fluid my-4">
      <TableManageLLMs />
    </div>
  );
}
