import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import TableManageContexts from "./TableManageContexts";

const ManageContextsPage = () => {
  useTopNavBarTitle("Manage Contexts");
  return (
    <div className="container my-4">
      <TableManageContexts />
    </div>
  );
};

export default ManageContextsPage;
