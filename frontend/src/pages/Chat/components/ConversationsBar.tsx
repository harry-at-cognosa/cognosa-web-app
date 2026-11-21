import { Button, ListGroup } from "react-bootstrap";
import { ChatDots, Pencil } from "react-bootstrap-icons";
import clsx from "clsx";
import { useChatStore } from "../stores/useChatStore";
import type { ChatConversation } from "../models";
import styles from "../ChatPage.module.css";

type Group = "Today" | "This week" | "Before";

function groupOf(iso: string): Group {
  const d = new Date(iso);
  const now = new Date();
  if (d.toDateString() === now.toDateString()) return "Today";
  if (d.getTime() >= now.getTime() - 7 * 24 * 60 * 60 * 1000) return "This week";
  return "Before";
}

function whenText(iso: string, group: Group): string {
  const d = new Date(iso);
  const time = d.toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
  if (group === "Today") return time;
  return (
    d.toLocaleDateString(undefined, { month: "short", day: "numeric" }) +
    ", " +
    time
  );
}

interface Props {
  onOpen: (conv_id: number) => void;
  onNew: () => void;
}

export default function ConversationsBar({ onOpen, onNew }: Props) {
  const store = useChatStore();
  const currentId = store.conv?.conv_id ?? null;

  const handleRename = async (item: ChatConversation) => {
    const title = window.prompt("Rename conversation", item.title);
    if (title === null || !title.trim() || title.trim() === item.title) return;
    try {
      await store.renameConversation(item.conv_id, title.trim());
    } catch {
      alert("Failed to rename the conversation. Please try again.");
    }
  };

  const handleDelete = async (item: ChatConversation) => {
    const name = item.title || "this conversation";
    if (!window.confirm(`Are you sure you want to delete "${name}"?`)) return;
    try {
      await store.deleteConversation(item.conv_id);
      if (item.conv_id === currentId) onNew();
    } catch {
      alert("Failed to delete the conversation. Please try again.");
    }
  };

  const groups: Group[] = ["Today", "This week", "Before"];
  return (
    <div className="w-100 bg-light border-end">
      <Button
        type="button"
        variant="light"
        className="w-100 fw-bold mt-2 btn-tc-300-400"
        disabled={store.streaming}
        onClick={onNew}
      >
        <ChatDots /> &nbsp; New Chat
      </Button>
      {groups.map((group) => {
        const rows = store.conversations.filter(
          (c) => groupOf(c.updated_at) === group,
        );
        if (!rows.length) return null;
        return (
          <div key={group}>
            <h5 className="p-2 mb-0 bg-opacity-10 bg-tc-100">{group}:</h5>
            <ListGroup as="ul" className="m-0">
              {rows.map((item) => (
                <ListGroup.Item
                  as="li"
                  key={item.conv_id}
                  className={clsx(
                    "p-2 border-bottom cursor-pointer list-group-item-action position-relative",
                    styles.item,
                    item.conv_id === currentId && styles.itemActive,
                  )}
                  onClick={() => {
                    // switching away would stop the answer being written
                    if (store.streaming || item.conv_id === currentId) return;
                    onOpen(item.conv_id);
                  }}
                >
                  <div className={styles.itemTitle} title={item.title}>
                    {item.title || <em className="text-muted">New chat</em>}
                  </div>
                  <div className={styles.meta}>
                    {whenText(item.updated_at, group)}
                  </div>
                  <span
                    className={clsx(
                      "position-absolute top-50 end-0 translate-middle-y me-1",
                      styles.itemActions,
                    )}
                  >
                    <Button
                      variant=""
                      size="sm"
                      className="p-1"
                      title="Rename"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRename(item);
                      }}
                    >
                      <Pencil size={13} />
                    </Button>
                    <Button
                      variant=""
                      size="sm"
                      className="p-1 delete-btn"
                      title="Delete"
                      disabled={store.streaming && item.conv_id === currentId}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(item);
                      }}
                    >
                      ×
                    </Button>
                  </span>
                </ListGroup.Item>
              ))}
            </ListGroup>
          </div>
        );
      })}
      {!store.conversations.length ? (
        <p className="text-muted p-3 mb-0">
          <em>No conversations yet.</em>
        </p>
      ) : null}
    </div>
  );
}
