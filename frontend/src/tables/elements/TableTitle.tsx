import type { createTableStore } from "../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableTitle({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;
  const title = data?.table_options?.title || tableStore.title;
  return (
    <h2 className="mr-1.5 ml-2 font-heading text-[22px] leading-none font-semibold tracking-[-0.015em] text-ink first:ml-1">
      {title}
    </h2>
  );
}
