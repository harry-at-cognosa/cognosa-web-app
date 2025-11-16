import { Form, InputGroup, Spinner } from "react-bootstrap";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useWebAppOptionsStore } from "../../../stores/useWebAppOptionsStore";
import {
  useDocTaskOptionsLastUsedStore,
  useDocTaskOptionsStore,
} from "../stores/useDocTaskOptionsStore";
import clsx from "clsx";
import { useEffect } from "react";

export default function QuerySelectLLM() {
  const current = useDocTasksCurrentStore();
  const { color } = useWebAppOptionsStore();
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const { gllms_id: lastUsedGLLMsID } = useDocTaskOptionsLastUsedStore();
  const waitingState = docTaskOptionsStore.needReload;
  const group_llms = docTaskOptionsStore.data.group_llms;
  useEffect(() => {
    if (waitingState) return;
    if (current.gllms_id === null) {
      // get first available gllms_id
      const all_gllms_id = group_llms.map((row) => Number(row.gllms_id));
      const defaultGLLMsID = all_gllms_id.includes(lastUsedGLLMsID || -999)
        ? lastUsedGLLMsID
        : Number(group_llms[0]?.gllms_id) || null;
      current.setGLLMsID(defaultGLLMsID);
    }
  }, [waitingState, current.gllms_id]);

  return (
    <InputGroup
      className={clsx("mb-2", {
        "d-none": !(group_llms.length > 1),
      })}
    >
      <InputGroup.Text
        id="input-group__query_documents__query_area__select_gllms_id"
        className="fw-bold"
        style={{ backgroundColor: color.c300 }}
      >
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
          disabled={waitingState}
        >
          {group_llms.map((gllms_obj) => (
            <option
              key={gllms_obj.gllms_id.toString()}
              value={gllms_obj.gllms_id.toString()}
            >
              {gllms_obj.gllms_name}
            </option>
          ))}
        </Form.Select>
      )}
    </InputGroup>
  );
}
