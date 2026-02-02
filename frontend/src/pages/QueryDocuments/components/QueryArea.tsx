import { useEffect } from "react";
import { Form, ProgressBar } from "react-bootstrap";
import axiosClient from "../../../api/axiosClient";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import type { DocTasksQuery } from "../models/docTasksQuery";
import type { DocTasksResponse } from "../models/docTasksResponse";
import { useDocTasksShortStore } from "../stores/useDocTasksShort";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import generateUUID from "../../../api/generateUUID";
import QuerySelectVDB from "./QuerySelectVDB";
import QuerySelectLLM from "./QuerySelectLLM";
import QuerySelectContext from "./QuerySelectContext";
import QueryTokensCounter from "./QueryTokensCounter";
import { useQueryDocumentsStore } from "../stores/useQueryDocumentStore";
import ContextJSON from "./ContextJSON";
import AskButton from "./AskButton";
import CloneQueryButton from "./CloneQueryButton";
import { useDocTasksGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useDocTasksGVDBsRetrParamsStore";
import DocTasksGVDBsRetrFilters from "./DocTasksGVDBsRetrFilters";

function QueryArea() {
  const queryStore = useQueryDocumentsStore();
  const gvdbsRetrParamsStore = useDocTasksGVDBsRetrParamsStore();
  const current = useDocTasksCurrentStore();
  const docTaskOptionsStore = useDocTaskOptionsStore();
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
    const gvdbs_row = docTaskOptionsStore.gvdbs_id__row[current.gvdbs_id];
    if (gvdbs_row.gvdbs_status === "danger") {
      alert(
        `Document Collection "${gvdbs_row.gvdbs_name}" is not ready to use`,
      );
      return;
    }
    if (!current.gllms_id) {
      alert("No LLM specified");
      return;
    }
    const gllms_row = docTaskOptionsStore.gllms_id__row[current.gllms_id];
    if (gllms_row.gllms_status === "danger") {
      alert(`LLM "${gllms_row.gllms_name}" is not ready to use`);
      return;
    }
    const gvdbs_cfg_json = gvdbsRetrParamsStore.getGVDBsRetrParamsDict();
    if (!gvdbs_cfg_json) {
      alert("No Document Search Options specified");
      return;
    }
    const query: DocTasksQuery = {
      doc_task_id: current.doc_task_id,
      short_name: current.short_name || "",
      input_text,
      gvdbs_id: current.gvdbs_id,
      gvdbs_cfg_json,
      gllms_id: current.gllms_id,
      gc_id: current.gc_id,
      optional_text: current.optional_text || "",
    };
    if (current.isSameAsPreviousQuery(query)) {
      alert("Query is the same as previous. Please, change something.");
      return;
    }
    try {
      current.setBeforeServerResponse(query);
      const opUUID = generateUUID();
      queryStore.setOpUUID(opUUID);
      const response = await axiosClient.post<DocTasksResponse>(
        "/doc_tasks",
        query,
      );
      if (useQueryDocumentsStore.getState().opUUID !== opUUID) return;
      const data = response.data;
      current.setFromServerResponse(data);
      gvdbsRetrParamsStore.copyFromDefault();
      gvdbsRetrParamsStore.setFromDocTaskData(data.gvdbs_cfg_json);
      startPolling(opUUID);
      docTasksShortStore.setNeedReload(true);
    } catch {
      alert("Error during post /doc_tasks");
      queryStore.stopPolling();
    }
  };

  // Poll /doc_tasks/<doc_task_id> until complete or error
  const startPolling = (uuid: string) => {
    if (!uuid) return;
    const poll = async () => {
      const doc_task_id = useDocTasksCurrentStore.getState().doc_task_id;
      if (!doc_task_id) return;
      try {
        const opUUID = generateUUID();
        queryStore.setOpUUID(opUUID);
        const response = await axiosClient.get<DocTasksResponse>(
          `doc_tasks/${doc_task_id}`,
        );
        if (useQueryDocumentsStore.getState().opUUID !== opUUID) return;
        const data = response.data;
        current.setFromServerResponse(data);
        gvdbsRetrParamsStore.copyFromDefault();
        gvdbsRetrParamsStore.setFromDocTaskData(data.gvdbs_cfg_json);
        // Continue polling until status becomes 6
        if (data.is_processing) {
          queryStore.setPollingTimeout(opUUID, startPolling);
        } else {
          queryStore.stopPolling();
        }
      } catch (error) {
        queryStore.stopPolling();
      }
    };
    poll();
  };

  // need reload (after select from history)
  useEffect(() => {
    if (!current.needReload) return;
    current.setNeedReload(false);
    const opUUID = generateUUID();
    queryStore.setOpUUID(opUUID);
    startPolling(opUUID);
  }, [current.needReload]);

  useEffect(() => {
    current.setNeedReload(true);
    return () => queryStore.stopPolling();
  }, []);

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
      <DocTasksGVDBsRetrFilters />
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
      <AskButton handleSubmit={handleSubmit} />
      <br className="mt-0" />
      <div style={{ visibility: queryStore.isPolling ? "visible" : "hidden" }}>
        <ProgressBar animated now={current.status_pct || 0} />
      </div>

      <h5>{current.status_text || ""}</h5>
      <div className="d-flex justify-content-between">
        <ContextJSON />
        <QueryTokensCounter />
        <CloneQueryButton />
      </div>
    </div>
  );
}

export default QueryArea;
