import { useState } from "react";
import { ChevronDown, Filter, RotateCcw } from "lucide-react";
import { Popover, PopoverTrigger } from "@/components/ui/popover";
import { EditorPopoverContent } from "./EditorPopover";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useDefaultGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useDefaultGVDBsRetrFiltersStore";
import { useModalGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useModalGVDBsRetrFiltersStore";
import GVDBsRetrFilters from "../../../components/GVDBsRetrFilters/GVDBsRetrFilters";
import { useDocTasksGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useDocTasksGVDBsRetrFiltersStore";
import { GVDBsRetrFiltersHistory } from "../../../components/GVDBsRetrFilters/history";

export default function DocTasksGVDBsRetrFilters() {
  const { doc_task_id, gvdbs_id } = useDocTasksCurrentStore();
  const DocTaskOptionsStore = useDocTaskOptionsStore();
  const [show, setShow] = useState(false);
  const defStore = useDefaultGVDBsRetrFiltersStore();
  const modalStore = useModalGVDBsRetrFiltersStore();
  const curStore = useDocTasksGVDBsRetrFiltersStore();

  // Filters exist only for collections that define them.
  const filtersAvailable =
    !DocTaskOptionsStore.needReload &&
    Boolean(defStore.isLoaded && defStore.fields) &&
    gvdbs_id !== -1;

  // Number of filter fields that hold a value; drives the active indicator.
  const activeCount = curStore.getDict()?.values.length || 0;

  const handleCancel = () => {
    setShow(false);
    modalStore.reset();
  };
  const handleApply = () => {
    setShow(false);
    const global_not_enabled = defStore.global_not_enabled || false;
    const fields = defStore.fields || [];
    GVDBsRetrFiltersHistory.update(
      doc_task_id,
      gvdbs_id,
      modalStore.global_not_value,
      modalStore.rf_field_id__values,
    );
    curStore.initData(
      { global_not_enabled, fields },
      modalStore.global_not_value,
      modalStore.rf_field_id__values,
    );
    modalStore.reset();
  };
  const handleShow = () => {
    if (show) return;
    // modal will show default values + current DocTask values.
    const {
      isLoaded: defLoaded,
      global_not_enabled: defGlobalNotEnabled,
      fields: defFields,
    } = defStore;
    if (!(defLoaded && defFields && defGlobalNotEnabled !== null)) return;

    modalStore.initData(
      {
        global_not_enabled: defGlobalNotEnabled,
        fields: defFields,
      },
      curStore.global_not_value,
      curStore.rf_field_id__values,
    );
    setShow(true);
  };

  if (!filtersAvailable) return null;

  return (
    <div className="flex min-w-0 items-center gap-1">
      {/* Apply commits; any other way of closing (X, Escape, click outside) discards */}
      <Popover
        open={show}
        onOpenChange={(open) => (open ? handleShow() : handleCancel())}
      >
        <PopoverTrigger asChild>
          <button
            type="button"
            className="pill"
            data-active={activeCount > 0}
            title={
              activeCount
                ? "Retrieval filters are limiting this query"
                : "No retrieval filters set"
            }
          >
            <Filter className="size-3.5 flex-none" />
            <span className="k">Retrieval Filters</span>
            {activeCount > 0 && <span className="count">{activeCount}</span>}
            <span className="v">{activeCount > 0 ? "active" : "none"}</span>
            <ChevronDown className="size-4 flex-none" />
          </button>
        </PopoverTrigger>
        <EditorPopoverContent
          title="Retrieval Filters"
          className="w-[600px]"
          onApply={handleApply}
        >
          <GVDBsRetrFilters />
        </EditorPopoverContent>
      </Popover>
      <button
        type="button"
        className="mini"
        onClick={() => {
          GVDBsRetrFiltersHistory.delete(doc_task_id, gvdbs_id);
          curStore.reset();
        }}
        title="Clears the Retrieval Filters"
      >
        <RotateCcw className="size-3.5" />
        Reset
      </button>
    </div>
  );
}
