import { useEffect } from "react";
import { LoaderCircle } from "lucide-react";
import { Table } from "@/components/ui/table";
import type { createTableStore } from "./TableStoreFactory";
import DeleteDialog from "./elements/DeleteDialog";
import EditDialog from "./elements/EditDialog";
import TableHeader from "./elements/TableHeader";
import TableToolbar from "./elements/TableToolbar";
import ReadRowDialog from "./elements/ReadRowDialog";
import TableBody from "./elements/TableBody";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function UniversalTable({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;

  useEffect(() => {
    if (!tableStore.needReload) return;
    tableStore.queryTable();
  }, [tableStore.needReload]);
  useEffect(() => tableStore.setNeedReload(true), []);

  if (!data && tableStore.busy === "read")
    return (
      <div className="flex justify-center py-10">
        <LoaderCircle
          className="size-8 animate-spin text-accent-text"
          role="status"
          aria-label="Loading"
        />
      </div>
    );

  return (
    <>
      {tableStore.error ? (
        <div
          role="alert"
          className="mb-3 rounded-2xl bg-err-bg px-3.5 py-2.5 text-sm font-medium wrap-break-word text-err"
        >
          {tableStore.error}
        </div>
      ) : null}
      {/* min-w-0: a wide table scrolls inside the card, never the page */}
      <div className="glass-card min-w-0 overflow-hidden rounded-3xl">
        <TableToolbar useStore={useStore} />
        <Table>
          <TableHeader useStore={useStore}></TableHeader>
          <TableBody useStore={useStore} />
        </Table>
      </div>
      <ReadRowDialog useStore={useStore}></ReadRowDialog>
      <EditDialog useStore={useStore}></EditDialog>
      <DeleteDialog useStore={useStore}></DeleteDialog>
    </>
  );
}
