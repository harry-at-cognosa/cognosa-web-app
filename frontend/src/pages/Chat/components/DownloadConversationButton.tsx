import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
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
    // usage, per answer and in total (answers only carry these figures)
    const n = (value: number | null) => (value ?? 0).toLocaleString("en-US");
    let totalIn = 0;
    let totalOut = 0;
    let totalSeconds = 0;
    let answers = 0;
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
        lines.push("");
        lines.push(
          `_Tokens: ${n(m.tokens_in)} in / ${n(m.tokens_out)} out` +
            (m.seconds !== null ? ` · ${m.seconds.toFixed(1)} s` : "") +
            "_",
        );
        totalIn += m.tokens_in ?? 0;
        totalOut += m.tokens_out ?? 0;
        totalSeconds += m.seconds ?? 0;
        answers += 1;
      }
      lines.push("");
    }

    lines.push("---");
    lines.push("");
    lines.push("## Totals");
    lines.push("");
    lines.push(`- Answers: ${answers}`);
    lines.push(`- Tokens in: ${n(totalIn)}`);
    lines.push(`- Tokens out: ${n(totalOut)}`);
    lines.push(`- Tokens in + out: ${n(totalIn + totalOut)}`);
    lines.push(`- Answer time: ${totalSeconds.toFixed(1)} s`);
    lines.push("");
    lines.push(
      "_Token counts are estimates made by Cognosa, not the LLM provider's " +
        "billed figures. They do not include the short extra call that restates " +
        "a follow-up question before searching._",
    );
    lines.push("");

    const fileName =
      `Chat${conv.conv_id}_` +
      `${sanitize(title).slice(0, 25).replace(/-+$/, "") || "conversation"}_` +
      `${timestamp(now)}.md`;
    await saveTextFile(fileName, lines.join("\n"));
  };

  return (
    <Button
      variant="outline"
      size="sm"
      className="ml-auto flex-none"
      disabled={!enabled}
      onClick={handleDownload}
      title="Download this conversation as a Markdown file"
    >
      <Download className="size-3.5" />
      Download
    </Button>
  );
}
