import type { createTableStore } from "../TableStoreFactory";
import HeaderColumnsRow from "./HeaderColumnsRow";
import HeaderFilterRow from "./HeaderFilterRow";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableHeader({ useStore }: Props) {
  return (
    <thead className="bg-sunk">
      <HeaderColumnsRow useStore={useStore} />
      <HeaderFilterRow useStore={useStore} />
    </thead>
  );
}
