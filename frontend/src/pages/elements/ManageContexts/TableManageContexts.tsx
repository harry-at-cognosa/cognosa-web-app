import React from "react";
import UniversalTable from "../../../tables/UniversalTable";
import { createTableStore } from "../../../tables/TableStoreFactory";

const useTableManageContextsStore = createTableStore();

export const TableManageContexts: React.FC = () => {
  return (
    <UniversalTable
      endpoint="/manage_contexts/query"
      request={{ name: "manage_contexts", limit: 10 }}
      useStore={useTableManageContextsStore}
    />
  );
};

export default TableManageContexts;
