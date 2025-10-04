import { useTopNavBarTitle } from "../hooks/useTopNavBarTitle";
import TableManageContexts from "./elements/ManageContexts/TableManageContexts";

const ManageContexts = () => {
  useTopNavBarTitle("Manage Contexts");
  return (
    <div className="container my-4">
      <h2>Group Contexts</h2>
      <TableManageContexts />
    </div>
  );
};

export default ManageContexts;
