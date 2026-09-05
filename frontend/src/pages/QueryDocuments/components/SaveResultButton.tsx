import { Button } from "react-bootstrap";
import { Download } from "react-bootstrap-icons";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { useQueryDocumentsStore } from "../stores/useQueryDocumentStore";
import type { DocTasksGVDBsCfgState } from "../../../components/GVDBsRetrParams/types";

// Feature 201 (phase 1): export the query shown on screen as a Markdown file.

const SHORT_NAME_MAX = 25;

function sanitize(text: string): string {
  return text
    .normalize("NFKD")
    .replace(/[^A-Za-z0-9_-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-+|-+$/g, "");
}

function timestamp(d: Date): string {
  const p = (n: number) => n.toString().padStart(2, "0");
  return (
    `${p(d.getFullYear() % 100)}${p(d.getMonth() + 1)}${p(d.getDate())}` +
    `_${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`
  );
}

function retrParamsShort(cfg: DocTasksGVDBsCfgState | null): string {
  if (!cfg?.search_kwargs) return "N/A";
  const k = cfg.search_kwargs;
  if (cfg.search_type === "similarity") return `SIM: ${k.k}`;
  if (cfg.search_type === "mmr")
    return `MMR: ${k.k}/${k.fetch_k}/${k.lambda_mult}`;
  if (cfg.search_type === "similarity_score_threshold")
    return `SST: ${k.k}/${k.score_threshold}`;
  return cfg.search_type;
}

function secondsOrNA(seconds: number | null) {
  return seconds === null ? "N/A" : `${seconds} sec`;
}

async function saveTextFile(fileName: string, text: string): Promise<void> {
  const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
  // Chrome / Edge: real "Save As" dialog (folder + editable name)
  const w = window as unknown as {
    showSaveFilePicker?: (opts: object) => Promise<{
      createWritable: () => Promise<{
        write: (b: Blob) => Promise<void>;
        close: () => Promise<void>;
      }>;
    }>;
  };
  if (typeof w.showSaveFilePicker === "function") {
    try {
      const handle = await w.showSaveFilePicker({
        suggestedName: fileName,
        types: [
          { description: "Markdown", accept: { "text/markdown": [".md"] } },
        ],
      });
      const writable = await handle.createWritable();
      await writable.write(blob);
      await writable.close();
      return;
    } catch (e) {
      if ((e as DOMException)?.name === "AbortError") return; // user cancelled
      // otherwise fall through to the download fallback
    }
  }
  // Safari / Firefox: browser download to the default folder
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export default function SaveResultButton() {
  const current = useDocTasksCurrentStore();
  const options = useDocTaskOptionsStore();
  const queryStore = useQueryDocumentsStore();

  const enabled =
    Boolean(current.output_text) &&
    !current.is_processing &&
    !queryStore.isPolling &&
    !current.needReloadFromHistory;

  const handleSave = async () => {
    const gvdbs = current.gvdbs_id ? options.gvdbs_id__row[current.gvdbs_id] : null;
    const gllms = current.gllms_id ? options.gllms_id__row[current.gllms_id] : null;
    const gc = options.data.group_contexts.find((r) => r.gc_id === current.gc_id);
    const collectionName = gvdbs?.gvdbs_name || "N/A";
    const collection = gvdbs?.gvdbs_collection || sanitize(collectionName) || "collection";
    const cfg = current.gvdbs_cfg_json;
    const { filters, ...cfgNoFilters } = cfg || ({} as DocTasksGVDBsCfgState);

    let docsFound: number | null = null;
    if (current.context_json) {
      try {
        const parsed = JSON.parse(current.context_json);
        if (Array.isArray(parsed)) docsFound = parsed.length;
      } catch {
        /* ignore */
      }
    }

    const shortName =
      current.short_name?.trim() ||
      (current.input_text || "").trim().slice(0, 35).trimEnd();
    const now = new Date();
    const fileName =
      `Q${current.doc_task_id ?? "new"}_` +
      `${sanitize(shortName).slice(0, SHORT_NAME_MAX).replace(/-+$/, "") || "query"}_` +
      `${sanitize(collection)}_${timestamp(now)}.md`;

    const lines: string[] = [];
    lines.push(`# Cognosa query result: Q${current.doc_task_id ?? ""} — ${shortName}`);
    lines.push("");
    lines.push(`Saved: ${now.toLocaleString()}`);
    lines.push("");
    lines.push("## 1. Query number and short name");
    lines.push(`- Query #: ${current.doc_task_id ?? "N/A"}`);
    lines.push(`- Short name: ${shortName || "none"}`);
    lines.push("");
    lines.push("## 2. Document collection");
    lines.push(`- Name: ${collectionName}`);
    lines.push(`- Collection: ${gvdbs?.gvdbs_collection || "N/A"}`);
    lines.push("");
    lines.push("## 3. Retrieval parameters");
    lines.push(`- ${retrParamsShort(cfg)}`);
    lines.push("");
    lines.push("```json");
    lines.push(JSON.stringify(cfgNoFilters, null, 2));
    lines.push("```");
    if (filters) {
      lines.push("");
      lines.push("Retrieval filters:");
      lines.push("");
      lines.push("```json");
      lines.push(JSON.stringify(filters, null, 2));
      lines.push("```");
    }
    lines.push("");
    lines.push("## 4. Query text");
    lines.push("");
    lines.push(current.input_text || "");
    lines.push("");
    lines.push("## 5. Context");
    lines.push(`- ${gc?.gc_name || "N/A"}`);
    lines.push("");
    lines.push("## 6. LLM");
    lines.push(`- ${gllms?.gllms_name || "N/A"}`);
    lines.push("");
    lines.push("## 7. Optional instruction");
    lines.push("");
    lines.push(current.optional_text?.trim() || "none");
    lines.push("");
    lines.push("## 8. Task status");
    lines.push(`- ${current.status_text || "N/A"}`);
    if (docsFound !== null) lines.push(`- Found documents (${docsFound})`);
    lines.push("");
    lines.push("## 9. Query performance");
    lines.push(
      `- VectorDB/LLM time: ${secondsOrNA(current.vdb_query_seconds)} / ` +
        `${secondsOrNA(current.llm_query_seconds)}`,
    );
    lines.push(
      `- Tokens Sent/Recv: ${current.llm_tokens_sent ?? "N/A"}/` +
        `${current.llm_tokens_received ?? "N/A"}`,
    );
    lines.push("");
    lines.push("## 10. Result");
    lines.push("");
    if (current.question_number >= 2 && current.output_text_2) {
      lines.push("### Answer 1");
      lines.push("");
      lines.push(current.output_text || "");
      lines.push("");
      lines.push("### Answer 2");
      lines.push("");
      lines.push(current.output_text_2);
    } else {
      lines.push(current.output_text || "");
    }
    lines.push("");

    await saveTextFile(fileName, lines.join("\n"));
  };

  return (
    <Button
      variant="outline-secondary"
      className="fw-bold ms-2 btn-tc-300-400"
      style={{ color: "black" }}
      disabled={!enabled}
      onClick={handleSave}
      title="Save the query and its result as a Markdown file"
    >
      <Download size="20px" style={{ marginBottom: "3px" }} /> Save Result
    </Button>
  );
}
