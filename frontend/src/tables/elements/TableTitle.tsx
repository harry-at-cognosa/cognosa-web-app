import type { createTableStore } from "../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableTitle({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;
  const title = data?.table_options?.title || tableStore.title;
  return <h3 className="mb-0">{title}</h3>;
}
