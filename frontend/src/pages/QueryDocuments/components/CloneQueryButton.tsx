import { Button } from "react-bootstrap";
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
      variant=""
      className="me-2 fw-bold btn-tc-300-400"
      size="sm"
      onClick={handleClick}
      disabled={disabled}
      style={{ visibility: visibility ? "visible" : "hidden" }}
    >
      Clone this query
    </Button>
  );
}
