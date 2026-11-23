import { Sel } from "@/components/Sel";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { useEffect } from "react";

export default function QuerySelectLLM() {
  const current = useDocTasksCurrentStore();
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const waitingState = docTaskOptionsStore.needReload;
  const group_llms = docTaskOptionsStore.data.group_llms;
  const lastUsedGLLMsID = current.previousQuery?.gllms_id || -999;
  useEffect(() => {
    if (waitingState) return;
    if (current.gllms_id === null) {
      // get first available gllms_id
      const all_gllms_id = group_llms.map((row) => Number(row.gllms_id));
      const defaultGLLMsID = all_gllms_id.includes(lastUsedGLLMsID)
        ? lastUsedGLLMsID
        : Number(group_llms[0]?.gllms_id) || null;
      current.setGLLMsID(defaultGLLMsID);
    }
  }, [waitingState, current.gllms_id]);

  function getOptionText(gllms_id: number | null): string {
    if (waitingState || !gllms_id) return "";
    const row = docTaskOptionsStore.gllms_id__row[gllms_id];
    if (!row) return "⛔ Not Found";
    if (row.gllms_status === "danger") return row.gllms_name + " ⛔";
    if (row.gllms_status === "warning") return row.gllms_name + " ⚠️";
    return row.gllms_name;
  }

  // v1.0.1: the LLM selector is hidden when the group has a single LLM
  if (!(group_llms.length > 1)) return null;

  return (
    <Sel
      variant="pill"
      label="LLM"
      value={waitingState ? "" : current.gllms_id?.toString() || ""}
      onChange={(v) => current.setGLLMsID(Number(v))}
      options={group_llms.map((gllms_obj) => ({
        value: gllms_obj.gllms_id.toString(),
        label: getOptionText(gllms_obj.gllms_id),
      }))}
      disabled={waitingState}
    />
  );
}
