import { Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";

export default function CloneQueryButton() {
  const { doc_task_id, previousQuery, is_processing, cloneQuery } =
    useDocTasksCurrentStore();
  const disabled = !doc_task_id || !previousQuery || is_processing !== false;
  const visibility = previousQuery && doc_task_id;
  function handleClick() {
    if (disabled) return;
    cloneQuery();
  }

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      onClick={handleClick}
      disabled={disabled}
      className={visibility ? undefined : "invisible"}
    >
      <Copy className="size-3.5" />
      Clone this query
    </Button>
  );
}
