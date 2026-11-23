import { useState } from "react";
import { Check } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";
import MarkdownRenderer from "../../../components/MarkdownRenderer";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useDocTasksShortStore } from "../stores/useDocTasksShort";
import { useQueryDocumentsStore } from "../stores/useQueryDocumentStore";
import { useAskedQuestion } from "../hooks/useAskedQuestion";
import { formatQueryDate } from "./QueriesListBarItem";
import CancelQueryButton from "./CancelQueryButton";
import CloneQueryButton from "./CloneQueryButton";
import ContextJSON from "./ContextJSON";
import QueryTokensCounter from "./QueryTokensCounter";
import SaveResultButton from "./SaveResultButton";

function ResponseArea() {
  const current = useDocTasksCurrentStore();
  const { doc_task_id, question_number, output_text, output_text_2 } = current;
  const isPolling = useQueryDocumentsStore((s) => s.isPolling);
  const rows = useDocTasksShortStore((s) => s.rows);
  const [showFirst, setShowFirst] = useState(false);
  const hasSecond = question_number >= 2;
  const content = hasSecond && !showFirst ? output_text_2 : output_text;
  const asked = useAskedQuestion(hasSecond && !showFirst ? 2 : 1);

  const created_at = rows.find((r) => r.doc_task_id === doc_task_id)?.created_at;
  const statusText = current.status_text || "";
  const statusKind = current.is_error
    ? "err"
    : current.is_processing
      ? "run"
      : statusText === "Task completed"
        ? "ok"
        : "off";

  return (
    <div>
      <div className="mx-1 mt-1.5 mb-1.5 flex items-baseline gap-2.5 text-[13px] text-muted-foreground">
        {doc_task_id !== null ? (
          <>
            <span>
              Query{" "}
              <b className="font-bold text-accent-text tabular-nums">
                {doc_task_id}
              </b>
            </span>
            {created_at && (
              <span className="tabular-nums">
                {formatQueryDate(created_at, true)}
              </span>
            )}
          </>
        ) : (
          <span>New Query</span>
        )}
      </div>
      {asked && (
        <h2 className="mx-1 mb-4 font-heading text-[27px] leading-[1.24] font-medium tracking-[-0.018em] wrap-anywhere whitespace-pre-line text-ink max-md:text-[21px]">
          {asked}
        </h2>
      )}

      <div className="glass-card rounded-3xl">
        {/* v1.0.1: the progress bar shows while the task is polled */}
        {isPolling && (
          <div
            className="border-b border-line-soft px-4 pt-3.5 pb-4"
            aria-live="polite"
          >
            <div className="flex items-center gap-2.5">
              <span className="status run whitespace-normal">
                {statusText || "…"}
              </span>
              <span className="ml-auto text-[13px] text-muted-foreground tabular-nums">
                {current.status_pct || 0}%
              </span>
            </div>
            <Progress
              value={current.status_pct || 0}
              className="my-3"
              aria-label="Query progress"
            />
            <CancelQueryButton />
          </div>
        )}

        <div className="flex flex-wrap items-center gap-2.5 px-4 py-3 empty:hidden">
          {!isPolling && statusText && (
            <span
              className={cn(
                "status h-auto min-h-7 whitespace-normal",
                statusKind,
                statusKind === "ok" && "plain pl-2",
              )}
              role="status"
            >
              {statusKind === "ok" && <Check className="size-3.5" />}
              {statusText}
            </span>
          )}
          <ContextJSON />
          {hasSecond ? (
            <ToggleGroup
              type="single"
              aria-label="Answer shown"
              value={showFirst ? "1" : "2"}
              onValueChange={(v) => v && setShowFirst(v === "1")}
            >
              <ToggleGroupItem value="1">Answer 1</ToggleGroupItem>
              <ToggleGroupItem value="2">Answer 2</ToggleGroupItem>
            </ToggleGroup>
          ) : null}
          <QueryTokensCounter />
        </div>

        <div className="border-t border-line-soft px-6 pt-[18px] pb-2 first:border-t-0 max-md:px-4">
          {content ? (
            <MarkdownRenderer content={content} />
          ) : (
            <p className="pb-2 text-muted-foreground">
              <em>Response will appear here...</em>
            </p>
          )}
        </div>

        <div className="flex flex-wrap justify-end gap-2 px-3.5 pt-1 pb-3.5">
          <CloneQueryButton />
          <SaveResultButton />
        </div>
      </div>
    </div>
  );
}

export default ResponseArea;
