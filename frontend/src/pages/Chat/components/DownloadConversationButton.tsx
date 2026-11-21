import { Button } from "react-bootstrap";
import { Download } from "react-bootstrap-icons";
import {
  sanitize,
  saveTextFile,
  timestamp,
} from "../../QueryDocuments/components/SaveResultButton";
import { useChatStore } from "../stores/useChatStore";

// The conversation as a Markdown file, built in the browser from the messages
// already on screen. Nothing is written on the server.
export default function DownloadConversationButton() {
  const store = useChatStore();
  const conv = store.conv;
  const enabled = Boolean(conv && store.messages.length && !store.streaming);

  const handleDownload = async () => {
    if (!conv) return;
    const collections = store.options?.collections || [];
    const llms = store.options?.llms || [];
    const collectionName =
      collections.find((c) => c.gvdbs_id === conv.gvdbs_id)?.gvdbs_name ||
      "N/A";
    const llmName = (gllms_id: number | null) =>
      llms.find((m) => m.gllms_id === gllms_id)?.gllms_name || "N/A";
    const title = conv.title || "Conversation";
    const now = new Date();

    const lines: string[] = [];
    lines.push(`# Cognosa conversation: ${title}`);
    lines.push("");
    lines.push(`- Conversation #: ${conv.conv_id}`);
    lines.push(`- Document collection: ${collectionName}`);
    if (conv.filters?.values?.length) {
      const not = conv.filters.global_not_value ? "NOT " : "";
      lines.push(
        "- Filters: " +
          conv.filters.values
            .map(
              (f) =>
                `${not}${f.short_title || f.rf_field_id} = ${f.values_list.join(" | ")}`,
            )
            .join("; "),
      );
    } else {
      lines.push("- Filters: none");
    }
    lines.push(`- Started: ${new Date(conv.created_at).toLocaleString()}`);
    lines.push(`- Saved: ${now.toLocaleString()}`);
    lines.push("");
    for (const m of store.messages) {
      const when = new Date(m.created_at).toLocaleString();
      lines.push("---");
      lines.push("");
      if (m.role === "user") {
        lines.push(`## Question (${when})`);
        lines.push("");
        lines.push(m.content);
      } else {
        const notes = [llmName(m.gllms_id), when];
        if (m.status === "stopped") notes.push("stopped before it finished");
        if (m.status === "error") notes.push("failed");
        lines.push(`## Answer (${notes.join(", ")})`);
        lines.push("");
        lines.push(m.content || "_No answer was written._");
      }
      lines.push("");
    }

    const fileName =
      `Chat${conv.conv_id}_` +
      `${sanitize(title).slice(0, 25).replace(/-+$/, "") || "conversation"}_` +
      `${timestamp(now)}.md`;
    await saveTextFile(fileName, lines.join("\n"));
  };

  return (
    <Button
      size="sm"
      variant="outline-secondary"
      className="fw-bold text-nowrap btn-tc-300-400"
      style={{ color: "black" }}
      disabled={!enabled}
      onClick={handleDownload}
      title="Download this conversation as a Markdown file"
    >
      <Download /> Download
    </Button>
  );
}
