import { Badge, Button, Form, ListGroup } from "react-bootstrap";
import type { DocTasksShortItem } from "../../../models/docTasksShortItem";
import { useDocTasksCurrentStore } from "./useDocTasksCurrent";
import axiosClient from "../../../api/axiosClient";
import { useDocTasksShortStore } from "./useDocTasksShort";

interface QueriesListBarItemProps {
  showDate: boolean;
  item: DocTasksShortItem;
}

function QueriesListBarItem({ item, showDate }: QueriesListBarItemProps) {
  const queriesStore = useDocTasksShortStore();
  const currentStore = useDocTasksCurrentStore();
  const loadQuery = (doc_task_id: number | null) => {
    if (doc_task_id === currentStore.doc_task_id) return;
    currentStore.setFromHistory(item);
  };
  if (!item.doc_task_id) return null;
  const formattedDate = showDate
    ? new Date(item.created_at).toLocaleDateString(undefined, {
        month: "short", // 'short' for month (e.g., "Jun")
        day: "numeric",
      }) +
      ", " +
      new Date(item.created_at).toLocaleTimeString()
    : new Date(item.created_at).toLocaleTimeString();

  // handle function: Delete this item
  const handleDelete = async (doc_task_id: number) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${item.short_name}"?`
    );

    if (!confirmed) return; // User canceled

    try {
      // 2. Send DELETE request
      await axiosClient.delete(`/doc_tasks/${doc_task_id}`);

      queriesStore.deleteRow(doc_task_id); // if such a method exists
    } catch (error) {
      console.error("Failed to delete query:", error);
      alert("Failed to delete query. Please try again.");
    }
  };
  return (
    <>
      <ListGroup.Item
        as="li"
        className="p-2 border-bottom cursor-pointer list-group-item-action position-relative"
        onClick={() => loadQuery(item.doc_task_id)}
      >
        {/* Timestamp Badge in top-right corner */}
        <Badge
          bg=""
          text="muted"
          className="position-absolute top-0 end-0 mt-0 me-2 pt-0 pe-1 small opacity-50"
        >
          {formattedDate}
        </Badge>

        <Form.Check type="radio">
          <Form.Check.Input
            type="radio"
            checked={item.doc_task_id === currentStore.doc_task_id}
            onChange={() => loadQuery(item.doc_task_id)}
          />
          <Form.Check.Label>{item.short_name}</Form.Check.Label>
        </Form.Check>
        {/* Delete button */}
        <Button
          variant=""
          size="sm"
          className="position-absolute top-50 end-0 translate-middle-y me-0 p-0 delete-btn"
          onClick={(e) => {
            e.stopPropagation(); // prevent triggering loadQuery
            handleDelete(item.doc_task_id);
          }}
        >
          ×
        </Button>
      </ListGroup.Item>
    </>
  );
}

export default QueriesListBarItem;
