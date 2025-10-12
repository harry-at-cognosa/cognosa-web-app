import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableManageContexts from "./TableManageContexts";

const ManageContextsPage = () => {
  useTopNavBarTitle("Manage Contexts");
  return (
    <div className="container my-4">
      <h2>Group Contexts</h2>
      <TableManageContexts />
    </div>
  );
};

export default ManageContextsPage;
