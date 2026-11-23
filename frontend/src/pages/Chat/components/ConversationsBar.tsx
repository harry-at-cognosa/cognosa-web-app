import { useRef, useState } from "react";
import { Pencil, X } from "lucide-react";
import { ConfirmDelete } from "@/components/ConfirmDelete";
import { GroupLabel } from "@/components/SplitLayout";
import { useChatStore } from "../stores/useChatStore";
import type { ChatConversation } from "../models";

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
  /** shows a failure message on the page */
  onNotice: (text: string) => void;
}

function ConversationItem({
  item,
  group,
  onOpen,
  onDelete,
  onNotice,
}: {
  item: ChatConversation;
  group: Group;
  onOpen: (conv_id: number) => void;
  onDelete: (item: ChatConversation) => void;
  onNotice: (text: string) => void;
}) {
  const store = useChatStore();
  const isCurrent = item.conv_id === (store.conv?.conv_id ?? null);
  const [renaming, setRenaming] = useState(false);
  const [title, setTitle] = useState(item.title);
  // Enter and Escape close the field, which also blurs it: act once only
  const closed = useRef(false);

  const startRename = () => {
    closed.current = false;
    setTitle(item.title);
    setRenaming(true);
  };
  const cancelRename = () => {
    closed.current = true;
    setRenaming(false);
  };
  // same rule as v1.0.1: an empty or unchanged title changes nothing
  const commitRename = async () => {
    if (closed.current) return;
    closed.current = true;
    setRenaming(false);
    const next = title.trim();
    if (!next || next === item.title) return;
    try {
      await store.renameConversation(item.conv_id, next);
    } catch {
      onNotice("Failed to rename the conversation. Please try again.");
    }
  };

  const when = (
    <span className="block text-[13px] text-muted-foreground tabular-nums">
      {whenText(item.updated_at, group)}
    </span>
  );

  return (
    <li className="hist-item" aria-current={isCurrent ? "true" : undefined}>
      {renaming ? (
        <div className="min-w-0">
          <input
            autoFocus
            aria-label="Rename conversation"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onFocus={(e) => e.currentTarget.select()}
            onBlur={commitRename}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.nativeEvent.isComposing) commitRename();
              if (e.key === "Escape") cancelRename();
            }}
            className="h-8 w-full rounded-lg border border-tint-edge bg-surface px-2 text-sm text-ink outline-none focus-visible:ring-3 focus-visible:ring-ring/40"
          />
          {when}
        </div>
      ) : (
        <button
          type="button"
          className="min-w-0 rounded-lg text-left"
          title={`Conversation ${item.conv_id}: ${item.title}`}
          onClick={() => {
            // switching away would stop the answer being written
            if (store.streaming || isCurrent) return;
            onOpen(item.conv_id);
          }}
        >
          {/* number first, as the Queries list does; it is the
              "Conversation #" of the download and of the page address */}
          <span className="line-clamp-2 leading-[1.3] wrap-anywhere text-ink">
            <b className="mr-1 font-bold text-accent-text tabular-nums">
              {item.conv_id}
            </b>
            {item.title || <em className="text-muted-foreground">New chat</em>}
          </span>
          {when}
        </button>
      )}
      <span className="flex items-center self-center">
        <button
          type="button"
          className="x-btn edit"
          title="Rename"
          aria-label={`Rename conversation ${item.conv_id}`}
          onClick={startRename}
        >
          <Pencil className="size-3.5" />
        </button>
        <button
          type="button"
          className="x-btn disabled:pointer-events-none disabled:opacity-40"
          title="Delete"
          aria-label={`Delete conversation ${item.conv_id}`}
          disabled={store.streaming && isCurrent}
          onClick={() => onDelete(item)}
        >
          <X className="size-3.5" />
        </button>
      </span>
    </li>
  );
}

export default function ConversationsBar({ onOpen, onNew, onNotice }: Props) {
  const store = useChatStore();
  const [deleting, setDeleting] = useState<ChatConversation | null>(null);

  const handleDelete = async (item: ChatConversation) => {
    const currentId = useChatStore.getState().conv?.conv_id ?? null;
    try {
      await store.deleteConversation(item.conv_id);
      if (item.conv_id === currentId) onNew();
    } catch {
      onNotice("Failed to delete the conversation. Please try again.");
    }
  };

  const groups: Group[] = ["Today", "This week", "Before"];
  return (
    <>
      {groups.map((group) => {
        const rows = store.conversations.filter(
          (c) => groupOf(c.updated_at) === group,
        );
        if (!rows.length) return null;
        return (
          <div key={group}>
            <GroupLabel>{group}:</GroupLabel>
            <ul>
              {rows.map((item) => (
                <ConversationItem
                  key={item.conv_id}
                  item={item}
                  group={group}
                  onOpen={onOpen}
                  onDelete={setDeleting}
                  onNotice={onNotice}
                />
              ))}
            </ul>
          </div>
        );
      })}
      {!store.conversations.length ? (
        <p className="px-2.5 py-3 text-sm text-muted-foreground">
          <em>No conversations yet.</em>
        </p>
      ) : null}
      <ConfirmDelete
        name={deleting ? deleting.title || "this conversation" : null}
        onCancel={() => setDeleting(null)}
        onConfirm={() => {
          const item = deleting;
          setDeleting(null);
          if (item) handleDelete(item);
        }}
      />
    </>
  );
}
