import { useEffect } from "react";
import { Table, Spinner, Alert } from "react-bootstrap";
import type { createTableStore } from "./TableStoreFactory";
import DeleteDialog from "./elements/DeleteDialog";
import EditDialog from "./elements/EditDialog";
import TableHeader from "./elements/TableHeader";
import ReadRowDialog from "./elements/ReadRowDialog";
import BusyModal from "./elements/BusyModal";
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
    return <Spinner animation="border" />;

  return (
    <>
      {tableStore.error ? (
        <Alert variant="danger">{tableStore.error}</Alert>
      ) : null}
      <Table bordered hover responsive>
        <TableHeader useStore={useStore}></TableHeader>
        <TableBody useStore={useStore} />
      </Table>
      <ReadRowDialog useStore={useStore}></ReadRowDialog>
      <EditDialog useStore={useStore}></EditDialog>
      <DeleteDialog useStore={useStore}></DeleteDialog>
      <BusyModal useStore={useStore}></BusyModal>
    </>
  );
}
