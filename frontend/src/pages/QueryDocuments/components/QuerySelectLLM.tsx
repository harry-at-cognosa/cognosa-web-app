import { Button, Form, InputGroup, Spinner } from "react-bootstrap";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import clsx from "clsx";
import { useEffect } from "react";
import { ArrowRepeat } from "react-bootstrap-icons";

export default function QuerySelectLLM() {
  const current = useDocTasksCurrentStore();
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const waitingState = docTaskOptionsStore.needReload;
  const group_llms = docTaskOptionsStore.data.group_llms;
  const lastUsedGLLMsID = current.previousQuery?.gllms_id || -999;
  useEffect(() => {
    if (waitingState) return;
    if (current.gllms_id === null) {
      // get first available gllms_id
      const all_gllms_id = group_llms.map((row) => Number(row.gllms_id));
      const defaultGLLMsID = all_gllms_id.includes(lastUsedGLLMsID)
        ? lastUsedGLLMsID
        : Number(group_llms[0]?.gllms_id) || null;
      current.setGLLMsID(defaultGLLMsID);
    }
  }, [waitingState, current.gllms_id]);

  function getSelectBgColor(gllms_id: number | null): string {
    if (waitingState || !gllms_id) return "";
    const row = docTaskOptionsStore.gllms_id__row[gllms_id];
    if (!row) return "#ECCCCF";
    if (row.gllms_status === "danger") return "#ECCCCF";
    if (row.gllms_status === "warning") return "#F2E7C3";
    return "";
  }

  function getOptionText(gllms_id: number | null): string {
    if (waitingState || !gllms_id) return "";
    const row = docTaskOptionsStore.gllms_id__row[gllms_id];
    if (!row) return "⛔ Not Found";
    if (row.gllms_status === "danger") return row.gllms_name + " ⛔";
    if (row.gllms_status === "warning") return row.gllms_name + " ⚠️";
    return row.gllms_name;
  }

  return (
    <InputGroup
      className={clsx("mb-2", {
        "d-none": !(group_llms.length > 1),
      })}
    >
      <InputGroup.Text
        id="input-group__query_documents__query_area__select_gllms_id"
        className="fw-bold bg-tc-300"
      >
        <Button
          type="button"
          variant=""
          className="p-0 me-2 fw-bold btn-tc-300-400"
          style={{ verticalAlign: "middle" }}
          onClick={() => docTaskOptionsStore.setNeedReload(true)}
          disabled={waitingState}
        >
          <ArrowRepeat size="20px" style={{ marginBottom: "3px" }} />
        </Button>
        LLM:
      </InputGroup.Text>
      {waitingState ? (
        <InputGroup.Text
          style={{
            flex: "1",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "#f8f9fa",
          }}
        >
          <Spinner animation="border" size="sm" />
        </InputGroup.Text>
      ) : (
        <Form.Select
          value={current.gllms_id?.toString() || ""}
          onChange={(e) => current.setGLLMsID(Number(e.target.value))}
          style={{ backgroundColor: getSelectBgColor(current.gllms_id) }}
        >
          {group_llms.map((gllms_obj) => (
            <option
              key={gllms_obj.gllms_id.toString()}
              value={gllms_obj.gllms_id.toString()}
              style={{ backgroundColor: getSelectBgColor(gllms_obj.gllms_id) }}
            >
              {getOptionText(gllms_obj.gllms_id)}
            </option>
          ))}
        </Form.Select>
      )}
    </InputGroup>
  );
}
