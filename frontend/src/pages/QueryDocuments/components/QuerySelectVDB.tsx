import { Form, InputGroup, Spinner } from "react-bootstrap";
import DocTasksGVDBsCfg from "./DocTasksGVDBsCfg";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useWebAppOptionsStore } from "../../../stores/useWebAppOptionsStore";
import {
  useDocTaskOptionsLastUsedStore,
  useDocTaskOptionsStore,
} from "../stores/useDocTaskOptionsStore";
import { useEffect } from "react";

export default function QuerySelectVDB() {
  const current = useDocTasksCurrentStore();
  const { color } = useWebAppOptionsStore();
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const { gvdbs_id: lastUsedGVDBsID } = useDocTaskOptionsLastUsedStore();
  const waitingState = docTaskOptionsStore.needReload;
  const group_vdbs = docTaskOptionsStore.data.group_vdbs;
  useEffect(() => {
    if (waitingState) return;
    if (current.gvdbs_id === null) {
      const all_gvdbs_id = group_vdbs.map((row) => Number(row.gvdbs_id));
      console.log(all_gvdbs_id);
      const defaultGVDBsID = all_gvdbs_id.includes(lastUsedGVDBsID || -999)
        ? lastUsedGVDBsID
        : Number(group_vdbs[0]?.gvdbs_id) || null;
      console.log(defaultGVDBsID);
      current.setGVDBsID(defaultGVDBsID);
    }
  }, [waitingState, current.gvdbs_id]);

  return (
    <InputGroup className="mb-2">
      <InputGroup.Text
        className="fw-bold"
        style={{ backgroundColor: color.c300 }}
      >
        Document Collection:
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
          value={current.gvdbs_id?.toString() || ""}
          onChange={(e) => current.setGVDBsID(Number(e.target.value))}
          disabled={waitingState}
        >
          {group_vdbs.map((gvdbs_obj) => (
            <option
              key={gvdbs_obj.gvdbs_id.toString()}
              value={gvdbs_obj.gvdbs_id.toString()}
            >
              {gvdbs_obj.gvdbs_name}
            </option>
          ))}
        </Form.Select>
      )}

      <DocTasksGVDBsCfg></DocTasksGVDBsCfg>
    </InputGroup>
  );
}
