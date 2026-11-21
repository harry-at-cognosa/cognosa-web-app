import { useEffect, useRef } from "react";
import { Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import clsx from "clsx";
import MarkdownRenderer from "../../../components/MarkdownRenderer";
import { useChatStore } from "../stores/useChatStore";
import type { ChatMessage, ChatQueryPrefill } from "../models";
import styles from "../ChatPage.module.css";

function UserBubble({ text }: { text: string }) {
  return (
    <div className={clsx(styles.row, styles.rowUser)}>
      <div className={styles.bubbleUser}>{text}</div>
    </div>
  );
}

function AssistantBubble({
  message,
  llmName,
  onOpenInQueries,
}: {
  message: ChatMessage;
  llmName: string;
  onOpenInQueries: (() => void) | null;
}) {
  const isError = message.status === "error";
  const meta = [
    llmName,
    message.seconds ? `${message.seconds.toFixed(1)} s` : "",
    message.status === "stopped" ? "Stopped" : "",
  ].filter(Boolean);
  return (
    <div className={styles.row}>
      <div className={styles.bubbleAssistant}>
        {isError ? (
          <div className={styles.errorText}>{message.content}</div>
        ) : message.content ? (
          <MarkdownRenderer content={message.content} />
        ) : (
          <em className="text-muted">No answer was written.</em>
        )}
        <div className={styles.meta}>
          {meta.join(" · ")}
          {onOpenInQueries ? (
            <>
              {meta.length ? " · " : ""}
              <button
                type="button"
                className={styles.linkButton}
                title="Start a query from this question, with the same collection and filters, on the Queries page"
                onClick={onOpenInQueries}
              >
                Open in Queries
              </button>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default function MessageThread() {
  const store = useChatStore();
  const navigate = useNavigate();
  const scrollRef = useRef<HTMLDivElement | null>(null);
  // Follow the answer while it is written, unless the reader scrolled up.
  const follow = useRef(true);

  useEffect(() => {
    const el = scrollRef.current;
    if (el && follow.current) el.scrollTop = el.scrollHeight;
  }, [store.messages, store.streamText, store.pendingUser, store.statusText]);

  // a message just sent, or another conversation opened: go to the bottom
  useEffect(() => {
    follow.current = true;
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [store.pendingUser, store.conv?.conv_id]);

  const llmName = (gllms_id: number | null) =>
    store.options?.llms.find((m) => m.gllms_id === gllms_id)?.gllms_name || "";
  const collectionName =
    store.options?.collections.find(
      (c) => c.gvdbs_id === (store.conv?.gvdbs_id ?? store.draftGvdbsId),
    )?.gvdbs_name || "";

  // Follow up on an answer with a full query: the question as it was actually
  // searched (the standalone form), on the conversation's collection and filters.
  const openInQueries = (m: ChatMessage) => {
    if (!store.conv || !m.retrieval_query) return;
    const chatPrefill: ChatQueryPrefill = {
      input_text: m.retrieval_query,
      gvdbs_id: store.conv.gvdbs_id,
      filters: store.conv.filters,
    };
    navigate("/app/query_documents/queries", { state: { chatPrefill } });
  };

  const isEmpty =
    !store.messages.length && store.pendingUser === null && !store.loadingConv;

  return (
    <div
      className={styles.thread}
      ref={scrollRef}
      onScroll={(e) => {
        const el = e.currentTarget;
        follow.current = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
      }}
    >
      {store.loadingConv ? (
        <div className={styles.empty}>
          <Spinner />
        </div>
      ) : isEmpty ? (
        <div className={styles.empty}>
          <h4>Ask a question</h4>
          {collectionName ? <p className="mb-0">{collectionName}</p> : null}
        </div>
      ) : (
        <div className={styles.threadInner}>
          {store.messages.map((m) =>
            m.role === "user" ? (
              <UserBubble key={m.msg_id} text={m.content} />
            ) : (
              <AssistantBubble
                key={m.msg_id}
                message={m}
                llmName={llmName(m.gllms_id)}
                onOpenInQueries={
                  m.retrieval_query && m.status !== "error" && !store.streaming
                    ? () => openInQueries(m)
                    : null
                }
              />
            ),
          )}
          {store.pendingUser !== null ? (
            <>
              <UserBubble text={store.pendingUser} />
              <div className={styles.row}>
                <div className={styles.bubbleAssistant}>
                  {store.streamText ? (
                    <MarkdownRenderer content={store.streamText} />
                  ) : null}
                  {store.streaming && !store.streamText ? (
                    <div className={styles.meta}>
                      <Spinner size="sm" className="me-2" />
                      {store.statusText || "Sending..."}
                    </div>
                  ) : null}
                </div>
              </div>
            </>
          ) : null}
        </div>
      )}
    </div>
  );
}
