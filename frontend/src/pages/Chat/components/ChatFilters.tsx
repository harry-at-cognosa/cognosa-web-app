import { useState } from "react";
import { CircleCheck, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import GVDBsRetrFilters from "../../../components/GVDBsRetrFilters/GVDBsRetrFilters";
import { useDefaultGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useDefaultGVDBsRetrFiltersStore";
import { useModalGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useModalGVDBsRetrFiltersStore";
import type { GVDBsRetrFiltersSchema } from "../../../components/GVDBsRetrFilters/types";
import { draftFiltersRequest, useChatStore } from "../stores/useChatStore";

export function parseFilterSchema(
  gvdbs_retr_filters: string | undefined,
): GVDBsRetrFiltersSchema | null {
  try {
    const parsed = JSON.parse(gvdbs_retr_filters || "{}");
    if (Array.isArray(parsed.fields) && parsed.fields.length)
      return {
        global_not_enabled: Boolean(parsed.global_not_enabled),
        fields: parsed.fields,
      };
  } catch {
    /* no usable schema: the collection has no filters */
  }
  return null;
}

// Filters for a chat that has not started. The form is the one the Queries
// page uses, driven by the collection's own filter schema; this component
// only feeds it and collects the result. Once the first message is sent the
// values are fixed and this button is no longer shown.
export default function ChatFilters({
  schemaStr,
}: {
  schemaStr: string | undefined;
}) {
  const store = useChatStore();
  const defStore = useDefaultGVDBsRetrFiltersStore();
  const modalStore = useModalGVDBsRetrFiltersStore();
  const [show, setShow] = useState(false);
  const schema = parseFilterSchema(schemaStr);
  if (!schema) return null; // this collection defines no filters

  const activeCount =
    draftFiltersRequest(store.draftFilters)?.values.length || 0;

  const handleShow = () => {
    // The form reads these two shared stores; load them for this collection.
    defStore.setDataFromString(schemaStr || "{}");
    modalStore.initData(
      schema,
      store.draftFilters.global_not_value,
      store.draftFilters.rf_field_id__values,
    );
    setShow(true);
  };
  const handleClose = () => {
    setShow(false);
    modalStore.reset();
  };
  const handleApply = () => {
    store.setDraftFilters({
      global_not_value: schema.global_not_enabled
        ? Boolean(modalStore.global_not_value)
        : null,
      rf_field_id__values: JSON.parse(
        JSON.stringify(modalStore.rf_field_id__values),
      ),
    });
    handleClose();
  };
  const handleClear = () => {
    store.setDraftFilters({ global_not_value: null, rf_field_id__values: {} });
    handleClose();
  };

  return (
    <>
      <button
        type="button"
        className="pill"
        data-active={activeCount > 0}
        disabled={store.streaming}
        onClick={handleShow}
        title={
          activeCount
            ? "Filters limit what this chat searches. They cannot be changed once the chat has started."
            : "Limit what this chat searches. Filters cannot be changed once the chat has started."
        }
      >
        <Filter className="size-3.5" />
        <span className="v">
          {activeCount ? `Filters: ${activeCount}` : "Filters"}
        </span>
      </button>

      <Dialog open={show} onOpenChange={(open) => !open && handleClose()}>
        <DialogContent className="max-h-[calc(100dvh-24px)] grid-rows-[auto_minmax(0,1fr)_auto] sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Filters for this chat</DialogTitle>
            <DialogDescription>
              Filters apply to every question in the chat and are fixed once the
              first message is sent.
            </DialogDescription>
          </DialogHeader>
          <div className="scroll-soft -mx-1 min-h-0 overflow-y-auto px-1">
            <GVDBsRetrFilters />
          </div>
          <DialogFooter className="sm:justify-center">
            <Button onClick={handleApply}>
              <CircleCheck />
              Apply
            </Button>
            <Button variant="outline" onClick={handleClear}>
              Clear all
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
