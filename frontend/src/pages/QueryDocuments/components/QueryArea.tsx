import { useState, useEffect } from "react";
import { Button, Form, ProgressBar } from "react-bootstrap";
import axiosClient from "../../../api/axiosClient";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import type { DocTasksQuery } from "../models/docTasksQuery";
import type { DocTasksResponse } from "../models/docTasksResponse";
import { useDocTasksShortStore } from "../stores/useDocTasksShort";
import {
  useDocTaskOptionsLastUsedStore,
  useDocTaskOptionsStore,
} from "../stores/useDocTaskOptionsStore";
import { useDocTasksGVDBsCfgStore } from "../stores/useDocTasksGVDBsCfg";
import generateUUID from "../../../api/generateUUID";
import QuerySelectVDB from "./QuerySelectVDB";
import QuerySelectLLM from "./QuerySelectLLM";
import QuerySelectContext from "./QuerySelectContext";
import QueryTokensCounter from "./QueryTokensCounter";

function QueryArea() {
  const gvdbsCfgStore = useDocTasksGVDBsCfgStore();
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [pollingInterval, setPollingInterval] = useState<number | null>(null);
  const current = useDocTasksCurrentStore();
  const currentOpUUID = useDocTasksCurrentStore((state) => state.opUUID);
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const docTaskOptionsLastUsedStore = useDocTaskOptionsLastUsedStore();
  const docTasksShortStore = useDocTasksShortStore();

  // Send POST request to url
  const handleSubmit = async () => {
    const input_text = current.input_text?.trim();
    if (!input_text) {
      alert("Enter query");
      return;
    }
    if (!current.gc_id) {
      alert("No context specified");
      return;
    }
    if (!current.gvdbs_id) {
      alert("No group vector DB specified");
      return;
    }
    if (!current.gllms_id) {
      alert("No LLM specified");
      return;
    }

    setIsProcessing(true);
    try {
      const query: DocTasksQuery = {
        short_name: current.short_name || "",
        input_text,
        gvdbs_id: current.gvdbs_id,
        gvdbs_cfg_json: {
          search_type: gvdbsCfgStore.search_type,
          search_kwargs: gvdbsCfgStore.search_kwargs,
        },
        gllms_id: current.gllms_id,
        gc_id: current.gc_id,
        optional_text: current.optional_text || "",
      };
      docTaskOptionsLastUsedStore.setLastUsed(
        current.gc_id,
        current.gllms_id,
        current.gvdbs_id
      );
      current.setBeforeServerResponse(query);
      const opUUID = generateUUID();
      current.setOpUUID(opUUID);
      const response = await axiosClient.post<DocTasksResponse>(
        "/doc_tasks",
        query
      );
      if (currentOpUUID !== opUUID) return;
      const data = response.data;
      current.setFromServerResponse(data);
      gvdbsCfgStore.setFromData(data.gvdbs_cfg_json);
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
        const opUUID = generateUUID();
        current.setOpUUID(opUUID);
        const response = await axiosClient.get<DocTasksResponse>(
          `doc_tasks/${doc_task_id}`
        );
        if (useDocTasksCurrentStore.getState().opUUID !== opUUID) return;
        const data = response.data;
        current.setFromServerResponse(data);
        gvdbsCfgStore.setFromData(data.gvdbs_cfg_json);
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
    if (!docTaskOptionsStore.needReload) return;
    async function fetchDocTaskOptions() {
      await docTaskOptionsStore.fetchData();
    }
    fetchDocTaskOptions();
  }, [docTaskOptionsStore.needReload]);
  useEffect(() => docTaskOptionsStore.setNeedReload(true), []);

  return (
    <div className="p-3 border-bottom bg-light">
      <QuerySelectVDB />
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
      <QuerySelectContext />
      <QuerySelectLLM />
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
      <QueryTokensCounter />
    </div>
  );
}

export default QueryArea;
