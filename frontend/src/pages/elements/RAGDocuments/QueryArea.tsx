import { useState, useEffect, useRef } from "react";
import { Button, Form, ProgressBar } from "react-bootstrap";
import type { groupContext } from "../../../models/groupContext";
import axiosClient from "../../../api/axiosClient";
import { useDocTasksCurrentStore } from "./useDocTasksCurrent";
import {
  useContextListStore,
  useContextListLastUsedStore,
} from "./useContextListStore";
import type { DocTasksQuery } from "../../../models/docTasksQuery";
import type { DocTasksResponse } from "../../../models/docTasksResponse";
import { useDocTasksShortStore } from "./useDocTasksShort";
import {
  useGroupVDBSLastUsedStore,
  useGroupVDBSStore,
} from "./useGroupVDBSStore";
import type { GroupVDBS } from "./groupVDBS";

function QueryArea() {
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [pollingInterval, setPollingInterval] = useState<number | null>(null);
  const current = useDocTasksCurrentStore();
  const contextListStore = useContextListStore();
  const contextListLastUsedStore = useContextListLastUsedStore();
  const groupVDBSStore = useGroupVDBSStore();
  const groupVDBSLastUsedStore = useGroupVDBSLastUsedStore();
  const docTasksShortStore = useDocTasksShortStore();
  const selectGCIDRef = useRef<HTMLSelectElement>(null);
  const selectGVDBSRef = useRef<HTMLSelectElement>(null);

  // Send POST request to url
  const handleSubmit = async () => {
    const input_text = current.input_text?.trim();
    if (!input_text) {
      alert("Enter query");
      return;
    }
    const gc_id = selectGCIDRef.current?.value
      ? Number(selectGCIDRef.current.value)
      : null;
    if (!gc_id) {
      alert("No context specified");
      return;
    }
    const gvdbs_id = selectGVDBSRef.current?.value
      ? Number(selectGVDBSRef.current.value)
      : null;
    if (!gvdbs_id) {
      alert("No group vector DB specified");
      return;
    }

    setIsProcessing(true);
    try {
      const query: DocTasksQuery = {
        short_name: current.short_name || "",
        input_text,
        gvdbs_id,
        gc_id,
        optional_text: current.optional_text || "",
      };
      contextListLastUsedStore.setGCID(current.gc_id);
      groupVDBSLastUsedStore.setGVDBSID(current.gvdbs_id);
      current.setBeforeServerResponse(query);
      const response = await axiosClient.post<DocTasksResponse>(
        "/doc_tasks",
        query
      );
      const data = response.data;
      current.setFromServerResponse(data);
      startPolling(data.doc_task_id);
      docTasksShortStore.setNeedReload(true);
    } catch {
      alert("Error during post /doc_tasks");
      setIsProcessing(false);
    }
  };

  // Poll /doc_tasks/<doc_task_id> until complete or error
  const startPolling = (doc_task_id: number | null) => {
    const poll = async () => {
      if (!doc_task_id) return;
      try {
        const response = await axiosClient.get<DocTasksResponse>(
          `doc_tasks/${doc_task_id}`
        );
        const data = response.data;
        current.setFromServerResponse(data);
        docTasksShortStore.setNeedReload(true);
        // Continue polling until status becomes 6
        if (data.is_processing) {
          const interval = setTimeout(poll, 1000);
          setPollingInterval(interval);
        } else {
          setIsProcessing(false);
          if (pollingInterval) {
            clearTimeout(pollingInterval);
            setPollingInterval(null);
          }
        }
      } catch (error) {
        setIsProcessing(false);
        if (pollingInterval) {
          clearTimeout(pollingInterval);
          setPollingInterval(null);
        }
      }
    };

    // Start first poll
    poll();
  };

  // need reload (after select from history)
  useEffect(() => {
    if (!current.needReload) return;
    current.setNeedReload(false);
    setIsProcessing(true);
    startPolling(current.doc_task_id);
  }, [current.needReload]);

  // Clean up polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearTimeout(pollingInterval);
      }
    };
  }, [pollingInterval]);

  useEffect(() => {
    if (!contextListStore.needReload) return;
    async function fetchGroupContexts() {
      try {
        const response = await axiosClient.get<groupContext[]>(
          "/group_contexts"
        );
        const rows = response.data;
        contextListStore.setRows(rows);
        if (!rows?.length) return;
        const all_gc_id = rows.map((row) => Number(row.gc_id));
        const defaultGCID = all_gc_id.includes(current.gc_id || -1)
          ? current.gc_id
          : Number(rows[0]?.gc_id) || null;
        current.setGCID(defaultGCID);
      } catch {
        alert("Error during fetching /group_contexts");
      }
    }
    fetchGroupContexts();
  }, [contextListStore.needReload]);

  useEffect(() => {
    if (!groupVDBSStore.needReload) return;
    async function fetchGroupVDBS() {
      try {
        const response = await axiosClient.get<GroupVDBS[]>("/group_vdbs");
        const rows = response.data;
        rows.sort((a, b) => {
          return (
            Number(b.gvdbs_status === "success") -
            Number(a.gvdbs_status === "success")
          );
        });
        groupVDBSStore.setRows(rows);
        if (!rows?.length) return;
        const all_gvdbs_id = rows.map((row) => Number(row.gvdbs_id));
        const defaultGVDBSID = all_gvdbs_id.includes(current.gvdbs_id || -1)
          ? current.gvdbs_id
          : Number(rows[0]?.gvdbs_id) || null;
        current.setGVDBSID(defaultGVDBSID);
      } catch {
        alert("Error during fetching /group_vdbs");
      }
    }
    fetchGroupVDBS();
  }, [groupVDBSStore.needReload]);

  return (
    <div className="p-3 border-bottom bg-light">
      <Form.Select
        ref={selectGVDBSRef}
        className="mb-2"
        value={current.gvdbs_id?.toString() || ""}
        onChange={(e) => current.setGVDBSID(Number(e.target.value))}
        style={{ display: groupVDBSStore.rows.length > 1 ? "inherit" : "none" }}
      >
        {groupVDBSStore.rows.map((gvdbs_obj) => (
          <option
            key={gvdbs_obj.gvdbs_id.toString()}
            value={gvdbs_obj.gvdbs_id.toString()}
          >
            {gvdbs_obj.gvdbs_name}
          </option>
        ))}
      </Form.Select>
      <Form.Control
        type="text"
        className="mb-2"
        placeholder="Query Short Name (optional)"
        value={current.short_name || ""}
        onChange={(e) => current.setShortName(e.target.value)}
      />
      <Form.Control
        as="textarea"
        className="mb-2"
        rows={4}
        placeholder="Enter your query here..."
        value={current.input_text || ""}
        onChange={(e) => current.setInputText(e.target.value)}
      />
      <Form.Select
        ref={selectGCIDRef}
        className="mb-2"
        value={current.gc_id?.toString() || ""}
        onChange={(e) => current.setGCID(Number(e.target.value))}
      >
        {contextListStore.rows.map((gc_obj) => (
          <option key={gc_obj.gc_id.toString()} value={gc_obj.gc_id.toString()}>
            {gc_obj.gc_name}
          </option>
        ))}
      </Form.Select>
      <Form.Control
        as="textarea"
        className="mb-2"
        rows={2}
        placeholder="Optional Instruction"
        value={current.optional_text || ""}
        onChange={(e) => current.setOptionalText(e.target.value)}
      />
      <Button
        onClick={handleSubmit}
        disabled={isProcessing}
        variant="outline-secondary"
        className="w-100"
      >
        Ask
      </Button>
      <br className="mt-0" />
      <div style={{ visibility: isProcessing ? "visible" : "hidden" }}>
        <ProgressBar animated now={current.status_pct || 0} />
      </div>
      <h5>{current.status_text || ""}</h5>
    </div>
  );
}

export default QueryArea;
