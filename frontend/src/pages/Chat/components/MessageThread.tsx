import { useEffect, useRef } from "react";
import { Spinner } from "react-bootstrap";
import clsx from "clsx";
import MarkdownRenderer from "../../../components/MarkdownRenderer";
import { useChatStore } from "../stores/useChatStore";
import type { ChatMessage } from "../models";
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
}: {
  message: ChatMessage;
  llmName: string;
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
        {meta.length ? (
          <div className={styles.meta}>{meta.join(" · ")}</div>
        ) : null}
      </div>
    </div>
  );
}

export default function MessageThread() {
  const store = useChatStore();
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
