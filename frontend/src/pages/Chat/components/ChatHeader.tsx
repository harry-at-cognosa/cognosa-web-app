import { Col, Form, Row } from "react-bootstrap";
import { useChatStore } from "../stores/useChatStore";
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

// Collection and LLM for the conversation. The collection can be chosen only
// before the first message: a conversation stays on one collection.
export default function ChatHeader() {
  const store = useChatStore();
  const collections = store.options?.collections || [];
  const llms = store.options?.llms || [];
  const started = store.conv !== null;
  const gvdbsId = started ? store.conv!.gvdbs_id : store.draftGvdbsId;
  const collection = collections.find((c) => c.gvdbs_id === gvdbsId);
  const llm = llms.find((m) => m.gllms_id === store.gllmsId);

  return (
    <div className={styles.header}>
      <Row className="g-2 align-items-center">
        <Col xs={12} md={7}>
          <Form.Select
            size="sm"
            aria-label="Document collection"
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
        </Col>
        <Col xs={12} md={5}>
          <Form.Select
            size="sm"
            aria-label="LLM"
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
        </Col>
      </Row>
    </div>
  );
}
