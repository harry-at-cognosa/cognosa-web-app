import { RefreshCw } from "lucide-react";
import { Sel } from "@/components/Sel";
import { cn } from "@/lib/utils";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { useEffect } from "react";
import { useDefaultGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useDefaultGVDBsRetrParamsStore";
import { useDocTasksGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useDocTasksGVDBsRetrParamsStore";
import { useDefaultGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useDefaultGVDBsRetrFiltersStore";
import { useDocTasksGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useDocTasksGVDBsRetrFiltersStore";

export default function QuerySelectVDB() {
  const current = useDocTasksCurrentStore();
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const defGVDBsRetrParamsStore = useDefaultGVDBsRetrParamsStore();
  const curGVDBsRetrParamsStore = useDocTasksGVDBsRetrParamsStore();
  const defGVDBsRetrFiltersStore = useDefaultGVDBsRetrFiltersStore();
  const curGVDBsRetrFiltersStore = useDocTasksGVDBsRetrFiltersStore();

  const waitingState = docTaskOptionsStore.needReload;
  const group_vdbs = docTaskOptionsStore.data.group_vdbs;
  const lastUsedGVDBsID = current.previousQuery?.gvdbs_id || -999;
  useEffect(() => {
    if (waitingState) return;
    if (current.gvdbs_id === null) {
      const all_gvdbs_id = group_vdbs.map((row) => Number(row.gvdbs_id));
      const defaultGVDBsID = all_gvdbs_id.includes(lastUsedGVDBsID)
        ? lastUsedGVDBsID
        : Number(group_vdbs[0]?.gvdbs_id) || null;
      current.setGVDBsID(defaultGVDBsID);
    }
  }, [waitingState, current.gvdbs_id]);

  // update gvdbs_retr_params from group_vdbs row if necessary.
  // A loaded query (previousQuery = last submitted query or the task loaded
  // from history) shows its own values on top of the collection defaults.
  // Otherwise the collection defaults are applied only when the collection
  // or its defaults changed, so parameters the user set by hand survive
  // "New Query". Runs independently of the Retrieval Filters effect below,
  // which flips its isLoaded flag on every poll.
  useEffect(() => {
    if (docTaskOptionsStore.needReload) return;
    if (!current.gvdbs_id || current.gvdbs_id === -1) return;
    const gvdbs_row = docTaskOptionsStore.gvdbs_id__row[current.gvdbs_id];
    const gvdbs_retr_params_str = gvdbs_row?.gvdbs_retr_params;
    if (!gvdbs_retr_params_str) return;
    defGVDBsRetrParamsStore.setData(gvdbs_retr_params_str);
    const defaultsKey = current.gvdbs_id + ":" + gvdbs_retr_params_str;
    const pq = current.previousQuery;
    if (pq && pq.gvdbs_id === current.gvdbs_id && pq.gvdbs_cfg_json) {
      curGVDBsRetrParamsStore.copyFromDefault();
      curGVDBsRetrParamsStore.setFromDocTaskData(
        JSON.stringify(pq.gvdbs_cfg_json),
      );
    } else if (
      useDocTasksGVDBsRetrParamsStore.getState().defaultsKey !== defaultsKey
    ) {
      curGVDBsRetrParamsStore.copyFromDefault();
    }
    curGVDBsRetrParamsStore.setDefaultsKey(defaultsKey);
  }, [
    docTaskOptionsStore.needReload,
    defGVDBsRetrParamsStore.isLoaded,
    current.gvdbs_id,
    current.previousQuery,
  ]);

  // update gvdbs_retr_filters from group_vdbs row + filters history
  useEffect(() => {
    if (docTaskOptionsStore.needReload) return;
    if (!current.gvdbs_id || current.gvdbs_id === -1) return;
    const gvdbs_row = docTaskOptionsStore.gvdbs_id__row[current.gvdbs_id];
    const gvdbs_retr_filters_str = gvdbs_row?.gvdbs_retr_filters;
    if (gvdbs_retr_filters_str) {
      defGVDBsRetrFiltersStore.setDataFromString(gvdbs_retr_filters_str);
      curGVDBsRetrFiltersStore.reset();
      curGVDBsRetrFiltersStore.loadFromRFHistory(
        current.doc_task_id,
        current.gvdbs_id,
        JSON.parse(gvdbs_retr_filters_str),
      );
    }
  }, [
    docTaskOptionsStore.needReload,
    defGVDBsRetrFiltersStore.isLoaded,
    current.doc_task_id,
    current.gvdbs_id,
  ]);

  function getOptionText(gvdbs_id: number | null): string {
    if (waitingState || !gvdbs_id) return "";
    const row = docTaskOptionsStore.gvdbs_id__row[gvdbs_id];
    if (!row) return "⛔ Not Found";
    if (row.gvdbs_status === "danger") return row.gvdbs_name + " ⛔";
    if (row.gvdbs_status === "warning") return row.gvdbs_name + " ⚠️";
    return row.gvdbs_name;
  }

  return (
    <div className="flex min-w-0 items-center gap-1">
      <Sel
        variant="pill"
        label="Document Collection"
        value={waitingState ? "" : current.gvdbs_id?.toString() || ""}
        onChange={(v) => current.setGVDBsID(Number(v))}
        options={group_vdbs.map((gvdbs_obj) => ({
          value: gvdbs_obj.gvdbs_id.toString(),
          label: getOptionText(gvdbs_obj.gvdbs_id),
        }))}
        disabled={waitingState}
      />
      <button
        type="button"
        className="mini"
        onClick={() => docTaskOptionsStore.setNeedReload(true)}
        disabled={waitingState}
        title="Reloads the Document Collection and LLM lists from the server"
      >
        <RefreshCw className={cn("size-3.5", waitingState && "animate-spin")} />
        Refresh lists
      </button>
    </div>
  );
}
