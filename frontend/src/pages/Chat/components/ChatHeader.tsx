import { useState } from "react";
import { Filter, Lock } from "lucide-react";
import { Sel } from "@/components/Sel";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { draftFiltersRequest, useChatStore } from "../stores/useChatStore";
import ChatFilters, { parseFilterSchema } from "./ChatFilters";

function statusMark(status: string): string {
  if (status === "danger") return "⛔ ";
  if (status === "warning") return "⚠️ ";
  return "";
}

// v1.0.1 tints the control when the chosen collection or LLM is not ready
function statusBg(status: string | undefined): string {
  if (status === "danger") return "bg-err-bg";
  if (status === "warning") return "bg-warn-bg";
  return "";
}

const LOCK_TEXT =
  "A conversation stays on one collection. Start a new chat to use another.";

interface FilterChip {
  key: string;
  title: string;
  value: string;
}

/** The collection once the chat has started: a locked pill. A click or tap shows why (hover alone fails on touch). */
function LockedCollection({ name, tint }: { name: string; tint: string }) {
  const [open, setOpen] = useState(false);
  return (
    <Tooltip open={open} onOpenChange={setOpen} disableHoverableContent>
      <TooltipTrigger asChild>
        <button
          type="button"
          className={"pill cursor-default! " + tint}
          data-locked="true"
          aria-label={`Document Collection: ${name}. ${LOCK_TEXT}`}
          onClick={(e) => {
            // Radix closes a tooltip on click; here the click is what shows it
            e.preventDefault();
            setOpen(true);
          }}
        >
          <Lock className="size-3.5" />
          <span className="k max-sm:hidden">Document Collection</span>
          <span className="v text-ink-2!">{name}</span>
        </button>
      </TooltipTrigger>
      <TooltipContent side="top" className="pointer-events-none">
        {LOCK_TEXT}
      </TooltipContent>
    </Tooltip>
  );
}

// Collection, filters and LLM for the conversation, shown under the message
// box. The collection and its filters can be chosen only before the first
// message: a conversation stays on one collection and one set of filter
// values. The LLM can change per turn.
export default function ChatSettings() {
  const store = useChatStore();
  const collections = store.options?.collections || [];
  const llms = store.options?.llms || [];
  const started = store.conv !== null;
  const gvdbsId = started ? store.conv!.gvdbs_id : store.draftGvdbsId;
  const collection = collections.find((c) => c.gvdbs_id === gvdbsId);
  const llm = llms.find((m) => m.gllms_id === store.gllmsId);

  // Filter values in force: stored ones for a started chat, the draft otherwise.
  const schema = parseFilterSchema(collection?.gvdbs_retr_filters);
  // the short title, as stored with a started conversation, so the label does
  // not change when the first message is sent
  const titleOf = (rf_field_id: string) => {
    const field = schema?.fields.find((f) => f.rf_field_id === rf_field_id) as
      | { title: string; short_title?: string | null }
      | undefined;
    return field?.short_title || field?.title || rf_field_id;
  };
  const filters = started
    ? store.conv!.filters
    : draftFiltersRequest(store.draftFilters);
  const chips: FilterChip[] = (filters?.values || []).map((f) => ({
    key: f.rf_field_id,
    title: f.short_title || titleOf(f.rf_field_id),
    value: f.values_list.join(" | "),
  }));
  const isNot = filters?.global_not_value === true;

  return (
    <div className="mt-1 flex flex-wrap items-center gap-2 border-t border-line-soft pt-3">
      {started ? (
        <LockedCollection
          name={
            collection
              ? statusMark(collection.gvdbs_status) + collection.gvdbs_name
              : "⛔ Collection not available"
          }
          tint={statusBg(collection?.gvdbs_status)}
        />
      ) : (
        <span
          className="inline-flex max-w-full min-w-0"
          title="Document collection for this chat"
        >
          <Sel
            variant="pill"
            label="Document Collection"
            className={statusBg(collection?.gvdbs_status)}
            disabled={store.streaming}
            value={gvdbsId === null ? "" : String(gvdbsId)}
            onChange={(v) => store.setDraftGvdbsId(Number(v))}
            options={collections.map((c) => ({
              value: String(c.gvdbs_id),
              label: statusMark(c.gvdbs_status) + c.gvdbs_name,
            }))}
          />
        </span>
      )}
      <span
        className="inline-flex max-w-full min-w-0"
        title="LLM that writes the next answer"
      >
        <Sel
          variant="pill"
          label="LLM"
          className={statusBg(llm?.gllms_status)}
          disabled={store.streaming}
          value={store.gllmsId === null ? "" : String(store.gllmsId)}
          onChange={(v) => store.setGllmsId(Number(v))}
          options={llms.map((m) => ({
            value: String(m.gllms_id),
            label: statusMark(m.gllms_status) + m.gllms_name,
          }))}
        />
      </span>
      {!started ? (
        <ChatFilters schemaStr={collection?.gvdbs_retr_filters} />
      ) : null}
      {chips.length ? (
        <div
          className="flex basis-full flex-wrap items-center gap-1.5"
          title={
            started
              ? "Filters of this conversation. They cannot be changed; start a new chat to use others."
              : "Filters for this chat. Fixed once the first message is sent."
          }
        >
          <Filter className="size-3.5 flex-none text-muted-foreground" aria-hidden />
          {isNot ? <span className="tag-not">NOT</span> : null}
          {chips.map((chip) => (
            <span key={chip.key} className="tag wrap-anywhere">
              {chip.title}: <b>{chip.value}</b>
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}
