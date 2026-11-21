import { Form } from "react-bootstrap";
import { FunnelFill } from "react-bootstrap-icons";
import { draftFiltersRequest, useChatStore } from "../stores/useChatStore";
import ChatFilters, { parseFilterSchema } from "./ChatFilters";
import DownloadConversationButton from "./DownloadConversationButton";
import styles from "../ChatPage.module.css";

function statusMark(status: string): string {
  if (status === "danger") return " ⛔";
  if (status === "warning") return " ⚠️";
  return "";
}

function statusBg(status: string | undefined): string {
  if (status === "danger") return "#ECCCCF";
  if (status === "warning") return "#F2E7C3";
  return "";
}

interface FilterChip {
  key: string;
  title: string;
  value: string;
}

// Collection, filters and LLM for the conversation. The collection and its
// filters can be chosen only before the first message: a conversation stays
// on one collection and one set of filter values. The LLM can change per turn.
export default function ChatHeader() {
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
    <div className={styles.header}>
      <div className="d-flex flex-wrap gap-2 align-items-center">
        <Form.Select
          size="sm"
          aria-label="Document collection"
          className={styles.headerCollection}
          title={
            started
              ? "A conversation stays on one collection. Start a new chat to use another."
              : "Document collection for this chat"
          }
          disabled={started || store.streaming}
          value={gvdbsId ?? ""}
          style={{ backgroundColor: statusBg(collection?.gvdbs_status) }}
          onChange={(e) => store.setDraftGvdbsId(Number(e.target.value))}
        >
          {started && !collection ? (
            <option value={gvdbsId ?? ""}>⛔ Collection not available</option>
          ) : null}
          {collections.map((c) => (
            <option key={c.gvdbs_id} value={c.gvdbs_id}>
              {c.gvdbs_name + statusMark(c.gvdbs_status)}
            </option>
          ))}
        </Form.Select>
        <Form.Select
          size="sm"
          aria-label="LLM"
          className={styles.headerLLM}
          title="LLM that writes the next answer"
          disabled={store.streaming}
          value={store.gllmsId ?? ""}
          style={{ backgroundColor: statusBg(llm?.gllms_status) }}
          onChange={(e) => store.setGllmsId(Number(e.target.value))}
        >
          {llms.map((m) => (
            <option key={m.gllms_id} value={m.gllms_id}>
              {m.gllms_name + statusMark(m.gllms_status)}
            </option>
          ))}
        </Form.Select>
        {!started ? (
          <ChatFilters schemaStr={collection?.gvdbs_retr_filters} />
        ) : null}
        <DownloadConversationButton />
      </div>
      {chips.length ? (
        <div
          className={styles.filterLine}
          title={
            started
              ? "Filters of this conversation. They cannot be changed; start a new chat to use others."
              : "Filters for this chat. Fixed once the first message is sent."
          }
        >
          <FunnelFill className="me-1" />
          {isNot ? <span className={styles.filterNot}>NOT</span> : null}
          {chips.map((chip) => (
            <span key={chip.key} className={styles.filterChip}>
              <strong>{chip.title}:</strong> {chip.value}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}
