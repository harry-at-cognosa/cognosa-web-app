import type { createTableStore } from "../TableStoreFactory";
import CreateRowButton from "./CreateRowButton";
import HeaderColumnsRow from "./HeaderColumnsRow";
import TableReloadButton from "./TableReloadButton";
import TableTitle from "./TableTitle";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableHeader({ useStore }: Props) {
  return (
    <thead>
      <tr>
        <th colSpan={100}>
          <div className="d-flex">
            <CreateRowButton useStore={useStore}></CreateRowButton>
            <TableTitle useStore={useStore}></TableTitle>
            <TableReloadButton useStore={useStore}></TableReloadButton>
          </div>
        </th>
      </tr>
      <HeaderColumnsRow useStore={useStore}></HeaderColumnsRow>
    </thead>
  );
}
