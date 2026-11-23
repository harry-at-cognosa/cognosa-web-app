import { useEffect, useRef, type ReactNode } from "react";
import { LoaderCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import MarkdownRenderer from "../../../components/MarkdownRenderer";
import { useChatStore } from "../stores/useChatStore";
import type { ChatMessage, ChatQueryPrefill } from "../models";

// Words in a table cell are not broken between letters: a wide table scrolls
// sideways inside the answer instead, as in v1.0.1.
const TABLE_WORDS = "[&_table]:wrap-normal";

function UserBubble({ text }: { text: string }) {
  return (
    <div className="max-w-[min(640px,88%)] self-end rounded-[22px_22px_6px_22px] border border-(--bubble-edge) bg-(--bubble) px-[18px] py-[11px] text-[15.5px] leading-normal wrap-anywhere whitespace-pre-wrap text-ink shadow-[0_12px_24px_-18px_var(--glow)]">
      {text}
    </div>
  );
}

function AnswerCard({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <article className={"glass-card min-w-0 rounded-3xl " + className}>
      {children}
    </article>
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
  return (
    <AnswerCard>
      <div className={"px-4 pt-4 pb-0.5 sm:px-6 " + TABLE_WORDS}>
        {isError ? (
          <div className="text-[15.5px] leading-normal wrap-anywhere text-err">
            {message.content}
          </div>
        ) : message.content ? (
          <MarkdownRenderer content={message.content} className="chat" />
        ) : (
          <em className="text-muted-foreground">No answer was written.</em>
        )}
      </div>
      <div className="flex flex-wrap items-center gap-x-3.5 gap-y-1 px-4 pt-2 pb-3 text-[13px] text-muted-foreground tabular-nums sm:px-6">
        {llmName ? <b className="font-semibold text-ink-2">{llmName}</b> : null}
        {message.seconds ? <span>{message.seconds.toFixed(1)} s</span> : null}
        {message.status === "stopped" ? <span>Stopped</span> : null}
        {onOpenInQueries ? (
          <button
            type="button"
            className="rounded text-accent-text underline underline-offset-2"
            title="Start a query from this question, with the same collection and filters, on the Queries page"
            onClick={onOpenInQueries}
          >
            Open in Queries
          </button>
        ) : null}
      </div>
    </AnswerCard>
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
      className="scroll-soft -mx-1 min-h-0 flex-1 overflow-y-auto px-1"
      ref={scrollRef}
      onScroll={(e) => {
        const el = e.currentTarget;
        follow.current = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
      }}
    >
      {store.loadingConv ? (
        <div className="flex h-full items-center justify-center">
          <LoaderCircle
            className="size-8 animate-spin text-accent-text"
            role="status"
            aria-label="Loading"
          />
        </div>
      ) : isEmpty ? (
        <div className="flex h-full flex-col items-center justify-center px-4 text-center text-muted-foreground">
          <h2 className="font-heading text-[22px] font-semibold tracking-[-0.015em] text-ink-2">
            Ask a question
          </h2>
          {collectionName ? (
            <p className="mt-1.5 wrap-anywhere">{collectionName}</p>
          ) : null}
        </div>
      ) : (
        <div className="flex flex-col gap-3.5 pb-2">
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
              {store.streamText || store.streaming ? (
                <AnswerCard className={store.streamText ? "" : "self-start"}>
                  {store.streamText ? (
                    <div className={"px-4 py-4 sm:px-6 " + TABLE_WORDS}>
                      <MarkdownRenderer content={store.streamText} className="chat" />
                    </div>
                  ) : null}
                  {store.streaming && !store.streamText ? (
                    <div className="flex items-center gap-2 px-4 py-3.5 text-[13px] text-muted-foreground sm:px-6">
                      <LoaderCircle
                        className="size-4 flex-none animate-spin text-accent-text"
                        role="status"
                        aria-label="Loading"
                      />
                      {store.statusText || "Sending..."}
                    </div>
                  ) : null}
                </AnswerCard>
              ) : null}
            </>
          ) : null}
        </div>
      )}
    </div>
  );
}
