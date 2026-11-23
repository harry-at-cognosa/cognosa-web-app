import { Sel } from "@/components/Sel";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { useEffect } from "react";

export default function QuerySelectContext() {
  const current = useDocTasksCurrentStore();
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const waitingState = docTaskOptionsStore.needReload;
  const group_contexts = docTaskOptionsStore.data.group_contexts;
  const lastUsedGCID = current.previousQuery?.gc_id || -999;
  useEffect(() => {
    if (waitingState) return;
    if (current.gc_id === null) {
      // get first available gc_id
      const all_gc_id = group_contexts.map((row) => Number(row.gc_id));
      const defaultGCID = all_gc_id.includes(lastUsedGCID)
        ? lastUsedGCID
        : Number(group_contexts[0]?.gc_id) || null;
      current.setGCID(defaultGCID);
    }
  }, [waitingState, current.gc_id]);

  return (
    <Sel
      variant="pill"
      label="Context"
      value={waitingState ? "" : current.gc_id?.toString() || ""}
      onChange={(v) => current.setGCID(Number(v))}
      options={group_contexts.map((gc_obj) => ({
        value: gc_obj.gc_id.toString(),
        label: gc_obj.gc_name,
      }))}
      disabled={waitingState || current.gvdbs_id === -1}
    />
  );
}
