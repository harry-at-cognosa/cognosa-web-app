import { useState } from "react";
import { ChevronDown, RotateCcw, SlidersHorizontal } from "lucide-react";
import { Popover, PopoverTrigger } from "@/components/ui/popover";
import { EditorPopoverContent } from "./EditorPopover";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import GVDBsRetrParams from "../../../components/GVDBsRetrParams/GVDBsRetrParams";
import { useDefaultGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useDefaultGVDBsRetrParamsStore";
import { useModalGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useModalGVDBsRetrParamsStore";
import { useDocTasksGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useDocTasksGVDBsRetrParamsStore";

export default function DocTasksGVDBsRetrParams() {
  const { gvdbs_id, needReloadFromHistory } = useDocTasksCurrentStore();
  const DocTaskOptionsStore = useDocTaskOptionsStore();
  const [show, setShow] = useState(false);
  const modalStore = useModalGVDBsRetrParamsStore();
  const defStore = useDefaultGVDBsRetrParamsStore();
  const curStore = useDocTasksGVDBsRetrParamsStore();

  if (DocTaskOptionsStore.needReload) return null;
  if (!defStore.isLoaded) return null;

  const modalDisabled = gvdbs_id === -1;

  const handleCancel = () => setShow(false);
  const handleApply = () => {
    const {
      search_type,
      search_kwargs__similarity,
      search_kwargs__mmr,
      search_kwargs__similarity_score_threshold,
    } = modalStore;
    if (
      !(
        search_type &&
        search_kwargs__similarity &&
        search_kwargs__mmr &&
        search_kwargs__similarity_score_threshold
      )
    )
      return;
    curStore.setData({
      search_type,
      search_kwargs__similarity: { ...search_kwargs__similarity },
      search_kwargs__mmr: { ...search_kwargs__mmr },
      search_kwargs__similarity_score_threshold: {
        ...search_kwargs__similarity_score_threshold,
      },
    });
    setShow(false);
  };
  const handleShow = () => {
    // modal will show default values + current DocTask values.
    const {
      isLoaded: defLoaded,
      search_type: defSearchType,
      search_kwargs__similarity: defSkSIM,
      search_kwargs__mmr: defSkMMR,
      search_kwargs__similarity_score_threshold: defSkSST,
    } = defStore;
    if (!(defLoaded && defSearchType && defSkSIM && defSkMMR && defSkSST))
      return;
    let newData = {
      search_type: defSearchType,
      search_kwargs__similarity: { ...defSkSIM },
      search_kwargs__mmr: { ...defSkMMR },
      search_kwargs__similarity_score_threshold: { ...defSkSST },
    };
    const {
      isLoaded: curLoaded,
      search_type: curSearchType,
      search_kwargs__similarity: curSkSIM,
      search_kwargs__mmr: curSkMMR,
      search_kwargs__similarity_score_threshold: curSkSST,
    } = curStore;
    if (curLoaded && curSearchType && curSkSIM && curSkMMR && curSkSST) {
      newData.search_type = curSearchType;
      if (curSearchType === "similarity")
        newData.search_kwargs__similarity = { ...curSkSIM };
      if (curSearchType === "mmr") newData.search_kwargs__mmr = { ...curSkMMR };
      if (curSearchType === "similarity_score_threshold")
        newData.search_kwargs__similarity_score_threshold = { ...curSkSST };
    }
    modalStore.setData(newData);

    setShow(true);
  };
  const shortName = modalDisabled
    ? "N/A"
    : needReloadFromHistory
      ? "…"
      : curStore.getShortName();

  return (
    <div className="flex min-w-0 items-center gap-1">
      {/* Apply commits; any other way of closing (X, Escape, click outside) discards */}
      <Popover
        open={show}
        onOpenChange={(open) => (open ? handleShow() : handleCancel())}
      >
        <PopoverTrigger asChild>
          <button type="button" className="pill" disabled={modalDisabled}>
            <SlidersHorizontal className="size-3.5 flex-none" />
            <span className="k">Retrieval Parameters</span>
            <span className="v tabular-nums">{shortName}</span>
            <ChevronDown className="size-4 flex-none" />
          </button>
        </PopoverTrigger>
        <EditorPopoverContent
          title="VDB Retrieval Parameters"
          className="w-[400px]"
          onApply={handleApply}
        >
          <GVDBsRetrParams />
        </EditorPopoverContent>
      </Popover>
      <button
        type="button"
        className="mini"
        onClick={() => {
          curStore.copyFromDefault();
        }}
        disabled={modalDisabled}
        title="Back to the collection's default Retrieval Parameters"
      >
        <RotateCcw className="size-3.5" />
        Reset
      </button>
    </div>
  );
}
