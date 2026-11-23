import { X } from "lucide-react";
import type { DocTasksShortItem } from "../models/docTasksShortItem";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useQueryDocumentsStore } from "../stores/useQueryDocumentStore";
import { useAsked } from "../hooks/useAskedQuestion";

interface QueriesListBarItemProps {
  showDate: boolean;
  item: DocTasksShortItem;
  /** asks for confirmation; the list owns the dialog and the delete itself */
  onDelete: (item: DocTasksShortItem) => void;
  /** called after a query was chosen (closes the list on a phone) */
  afterPick?: () => void;
}

// eslint-disable-next-line react-refresh/only-export-components
export function formatQueryDate(created_at: string, showDate: boolean) {
  return showDate
    ? new Date(created_at).toLocaleDateString(undefined, {
        month: "short", // 'short' for month (e.g., "Jun")
        day: "numeric",
      }) +
        ", " +
        new Date(created_at).toLocaleTimeString()
    : new Date(created_at).toLocaleTimeString();
}

function QueriesListBarItem({
  item,
  showDate,
  onDelete,
  afterPick,
}: QueriesListBarItemProps) {
  const queryStore = useQueryDocumentsStore();
  const currentStore = useDocTasksCurrentStore();
  const loadQuery = (doc_task_id: number | null) => {
    if (doc_task_id === currentStore.doc_task_id) return;
    queryStore.setOpUUID("");
    useAsked.getState().setPending(null);
    currentStore.setFromHistory(item);
  };
  if (!item.doc_task_id) return null;
  const formattedDate = formatQueryDate(item.created_at, showDate);
  const isCurrent = item.doc_task_id === currentStore.doc_task_id;

  return (
    <li className="hist-item" aria-current={isCurrent ? "true" : undefined}>
      <button
        type="button"
        className="min-w-0 rounded-lg text-left"
        onClick={() => {
          loadQuery(item.doc_task_id);
          afterPick?.();
        }}
      >
        <span className="line-clamp-2 leading-[1.3] wrap-anywhere text-ink">
          <b className="mr-1 font-bold text-accent-text tabular-nums">
            {item.doc_task_id}
          </b>
          {item.short_name}
        </span>
        <span className="block text-[13px] text-muted-foreground tabular-nums">
          {formattedDate}
        </span>
      </button>
      <button
        type="button"
        className="x-btn self-center"
        aria-label={`Delete query ${item.doc_task_id}`}
        onClick={() => onDelete(item)}
      >
        <X className="size-3.5" />
      </button>
    </li>
  );
}

export default QueriesListBarItem;
