import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import type { createTableStore } from "../TableStoreFactory";
import RowValues from "./RowValues";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function DeleteDialog({ useStore }: Props) {
  const tableStore = useStore();
  const { data, deleteRow, setDeleteRow } = tableStore;
  if (!data) return null;
  if (!deleteRow) return null;
  const { delete__ask_columns } = data.table_options;
  const handleClose = () => setDeleteRow(null);
  return (
    <Dialog
      open={Boolean(deleteRow)}
      onOpenChange={(open) => {
        if (!open) handleClose();
      }}
    >
      <DialogContent
        className="flex max-h-[calc(100dvh-2rem)] flex-col gap-0 overflow-hidden p-0 sm:max-w-[520px]"
        onOpenAutoFocus={(e) => {
          e.preventDefault();
          (e.currentTarget as HTMLElement).focus();
        }}
      >
        <div className="px-5 pt-5 pr-14 pb-3">
          <DialogTitle>Confirm delete:</DialogTitle>
          <DialogDescription className="sr-only">
            Values of the row that will be deleted
          </DialogDescription>
        </div>
        <div className="scroll-soft min-h-0 flex-1 overflow-y-auto px-5 pb-4">
          <RowValues
            useStore={useStore}
            row={deleteRow}
            cols={delete__ask_columns}
          />
        </div>
        <div className="flex flex-none justify-end border-t border-line-soft px-5 py-3.5">
          <Button
            variant="destructive"
            onClick={tableStore.queryDeleteRow}
            disabled={tableStore.busy != ""}
          >
            Delete
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
