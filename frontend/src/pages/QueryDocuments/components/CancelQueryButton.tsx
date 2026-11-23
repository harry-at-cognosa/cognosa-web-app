import { useState } from "react";
import { Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import axiosClient from "../../../api/axiosClient";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useQueryDocumentsStore } from "../stores/useQueryDocumentStore";
import type { DocTasksResponse } from "../models/docTasksResponse";
import { useQueryNotice } from "../hooks/useQueryNotice";

/**
 * Cancel the in-flight query. POST /doc_tasks/{id}/cancel moves the task to a
 * terminal "Cancelled by user" status; the run_tasks writers are guarded on
 * status, so the LLM stream stops at its next chunk. The regular poll then
 * picks up the terminal row and stops on its own.
 */
export default function CancelQueryButton() {
  const current = useDocTasksCurrentStore();
  const queryStore = useQueryDocumentsStore();
  const [busy, setBusy] = useState(false);
  const visible = queryStore.isPolling && current.is_processing === true;
  if (!visible) return null;

  async function handleClick() {
    const doc_task_id = current.doc_task_id;
    if (!doc_task_id || busy) return;
    setBusy(true);
    try {
      const response = await axiosClient.post<DocTasksResponse>(
        `/doc_tasks/${doc_task_id}/cancel`,
      );
      current.setFromServerResponse(response.data);
      if (!response.data.is_processing) queryStore.stopPolling();
    } catch {
      useQueryNotice
        .getState()
        .show("Could not cancel the query. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      onClick={handleClick}
      disabled={busy}
    >
      <Square className="size-3" />
      Cancel this query
    </Button>
  );
}
