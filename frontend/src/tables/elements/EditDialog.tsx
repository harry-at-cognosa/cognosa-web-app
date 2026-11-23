import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import type { createTableStore } from "../TableStoreFactory";
import BusyModal from "./BusyModal";
import EditCellElement from "./EditCellElement";
import ExportButton from "./ExportButton";
import ColumnDisplayName from "./ColumnDisplayName";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

function EditMsg({ msg, key_ }: { msg: string; key_: string }) {
  const text_lines = msg
    .trim()
    .split("\n")
    .map((x) => x.trim());
  return (
    <div className="mt-1.5 px-0.5 text-[13px] text-muted-foreground" key={key_}>
      {text_lines.map((line, i) => (
        <div key={key_ + "__line_" + i}>{line}</div>
      ))}
    </div>
  );
}

// column types whose editor needs the full width of the form
const WIDE_TYPES = [
  "text",
  "api_settings_value",
  "gvdbs_retr_params",
  "gvdbs_retr_filters",
];

// column types edited in a multi-line text box
const LONG_TEXT_TYPES = ["text", "gvdbs_retr_filters"];

export default function EditDialog({ useStore }: Props) {
  const tableStore = useStore();
  const { data, showCreateOrUpdateDialog } = tableStore;
  if (!data) return null;
  if (!showCreateOrUpdateDialog) return null;
  const isCreate = showCreateOrUpdateDialog === "create";
  const { create__ask_columns, update__ask_columns } = data.table_options;
  const ask_columns = isCreate ? create__ask_columns : update__ask_columns;
  const handleClose = () => tableStore.setShowCreateOrUpdateDialog("", null);
  const haveErrors = !!Object.keys(tableStore.editRowErrorMsg).length;
  // while the request is pending the dialog cannot be closed (v1.0.1: static modal on top)
  const isPending =
    tableStore.busy === "create_pending" ||
    tableStore.busy === "update_pending";
  const oneColumn = ask_columns.length < 2;
  // a form with a long-text field is as wide as v1.0.1's dialog (1140 px)
  const hasLongText = ask_columns.some((col) =>
    LONG_TEXT_TYPES.includes(data.columns[col].type),
  );
  return (
    <Dialog
      open={Boolean(showCreateOrUpdateDialog)}
      onOpenChange={(open) => {
        if (!open && !isPending) handleClose();
      }}
    >
      <DialogContent
        className={cn(
          "flex max-h-[calc(100dvh-2rem)] flex-col gap-0 overflow-hidden p-0",
          hasLongText
            ? "sm:max-w-[min(1140px,calc(100%-2rem))]"
            : "sm:max-w-[min(860px,calc(100%-2rem))]",
        )}
        onOpenAutoFocus={(e) => {
          e.preventDefault();
          (e.currentTarget as HTMLElement).focus();
        }}
      >
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 px-5 pt-5 pr-14 pb-3">
          <DialogTitle>{isCreate ? "Add new:" : "Edit:"}</DialogTitle>
          <DialogDescription className="sr-only">
            {isCreate ? "Values of the new row" : "Values of the row"}
          </DialogDescription>
          {haveErrors ? (
            <span className="font-bold text-err">Found errors!</span>
          ) : null}
          <span className="flex-1" />
          {tableStore.editRow ? (
            <ExportButton useStore={useStore} row={tableStore.editRow} />
          ) : null}
        </div>
        <div className="scroll-soft min-h-0 flex-1 overflow-y-auto px-5 pt-1 pb-4">
          {tableStore.error ? (
            <div
              role="alert"
              className="mb-3 rounded-2xl bg-err-bg px-3.5 py-2.5 text-sm font-medium wrap-break-word text-err"
            >
              {tableStore.error}
            </div>
          ) : null}
          <div
            className={cn(
              "grid gap-x-4 gap-y-3.5",
              oneColumn ? "grid-cols-1" : "grid-cols-2",
            )}
          >
            {ask_columns.map((col) => (
              <div
                key={"div__" + col}
                className={cn(
                  "min-w-0",
                  !oneColumn &&
                    WIDE_TYPES.includes(data.columns[col].type) &&
                    "col-span-2",
                )}
              >
                <div className="lbl" key={"div_label__" + col}>
                  <label htmlFor={"edit_cell_element__" + col}>
                    <ColumnDisplayName
                      nameType="dialog"
                      col={col}
                      data={data}
                    />
                    {data.columns[col].cu_required ? (
                      <span className="text-err">*</span>
                    ) : null}
                  </label>
                  {tableStore.editRowErrorMsg[col] ? (
                    <span
                      className="ml-3 text-err"
                      key={"div_error_msg__" + col}
                    >
                      {tableStore.editRowErrorMsg[col]}
                    </span>
                  ) : null}
                </div>
                <div key={"div_value__" + col}>
                  <EditCellElement
                    useStore={useStore}
                    col={col}
                  ></EditCellElement>
                </div>
                {data.columns[col].cu_edit_msg ? (
                  <EditMsg
                    msg={data.columns[col].cu_edit_msg}
                    key_={"div_desc__" + col}
                  />
                ) : null}
              </div>
            ))}
          </div>
        </div>
        <div className="flex flex-none justify-end border-t border-line-soft px-5 py-3.5">
          <Button
            size="lg"
            onClick={tableStore.queryEditRow}
            disabled={tableStore.busy != ""}
          >
            Save
          </Button>
        </div>
        <BusyModal useStore={useStore}></BusyModal>
      </DialogContent>
    </Dialog>
  );
}
