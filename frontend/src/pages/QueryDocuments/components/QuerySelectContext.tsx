import { Form, InputGroup, Spinner } from "react-bootstrap";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useWebAppOptionsStore } from "../../../stores/useWebAppOptionsStore";
import {
  useDocTaskOptionsLastUsedStore,
  useDocTaskOptionsStore,
} from "../stores/useDocTaskOptionsStore";
import { useEffect } from "react";

export default function QuerySelectContext() {
  const current = useDocTasksCurrentStore();
  const { color } = useWebAppOptionsStore();
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const { gc_id: lastUsedGCID } = useDocTaskOptionsLastUsedStore();
  const waitingState = docTaskOptionsStore.needReload;
  const group_contexts = docTaskOptionsStore.data.group_contexts;
  useEffect(() => {
    if (waitingState) return;
    if (current.gc_id === null) {
      // get first available gc_id
      const all_gc_id = group_contexts.map((row) => Number(row.gc_id));
      const defaultGCID = all_gc_id.includes(lastUsedGCID || -999)
        ? lastUsedGCID
        : Number(group_contexts[0]?.gc_id) || null;
      current.setGCID(defaultGCID);
    }
  }, [waitingState, current.gc_id]);

  return (
    <InputGroup className="mb-2">
      <InputGroup.Text
        className="fw-bold"
        style={{ backgroundColor: color.c300 }}
      >
        Context:
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
          value={current.gc_id?.toString() || ""}
          onChange={(e) => current.setGCID(Number(e.target.value))}
          disabled={waitingState || current.gvdbs_id === -1}
        >
          {group_contexts.map((gc_obj) => (
            <option
              key={gc_obj.gc_id.toString()}
              value={gc_obj.gc_id.toString()}
            >
              {gc_obj.gc_name}
            </option>
          ))}
        </Form.Select>
      )}
    </InputGroup>
  );
}
