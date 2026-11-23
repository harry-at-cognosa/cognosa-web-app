import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import type { createTableStore } from "../TableStoreFactory";
import ExportButton from "./ExportButton";
import RowValues from "./RowValues";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function ReadRowDialog({ useStore }: Props) {
  const tableStore = useStore();
  const { data, readRow, setReadRow } = tableStore;
  if (!data) return null;
  if (!readRow) return null;
  const { read__visible_columns, view__visible_columns } = data.table_options;
  const visible_columns = view__visible_columns || read__visible_columns;
  const handleClose = () => setReadRow(null);
  return (
    <Dialog
      open={Boolean(readRow)}
      onOpenChange={(open) => {
        if (!open) handleClose();
      }}
    >
      <DialogContent
        className="flex max-h-[calc(100dvh-2rem)] flex-col gap-0 overflow-hidden p-0 sm:max-w-[800px]"
        onOpenAutoFocus={(e) => {
          e.preventDefault();
          (e.currentTarget as HTMLElement).focus();
        }}
      >
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 px-5 pt-5 pr-14 pb-3">
          <DialogTitle>Row values:</DialogTitle>
          <DialogDescription className="sr-only">
            All values of the row
          </DialogDescription>
          <span className="flex-1" />
          <ExportButton useStore={useStore} row={readRow} />
        </div>
        <div className="scroll-soft min-h-0 flex-1 overflow-y-auto px-5 pb-4">
          <RowValues
            useStore={useStore}
            row={readRow}
            cols={visible_columns}
          />
        </div>
        <div className="flex flex-none justify-end border-t border-line-soft px-5 py-3.5">
          <Button variant="outline" onClick={handleClose}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
