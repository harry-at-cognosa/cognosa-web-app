import { Button, Form, InputGroup, Spinner } from "react-bootstrap";
import DocTasksGVDBsRetrParams from "./DocTasksGVDBsRetrParams";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { useEffect } from "react";
import { ArrowRepeat } from "react-bootstrap-icons";
import { useDefaultGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useDefaultGVDBsRetrParamsStore";
import { useDocTasksGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useDocTasksGVDBsRetrParamsStore";
import { useLoggedUserStore } from "../../../stores/useLoggedUserStore";
import { useDefaultGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useDefaultGVDBsRetrFiltersStore";

export default function QuerySelectVDB() {
  const user = useLoggedUserStore();
  const current = useDocTasksCurrentStore();
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const defGVDBsRetrParamsStore = useDefaultGVDBsRetrParamsStore();
  const curGVDBsRetrParamsStore = useDocTasksGVDBsRetrParamsStore();
  const defGVDBsRetrFiltersStore = useDefaultGVDBsRetrFiltersStore();

  const waitingState = docTaskOptionsStore.needReload;
  const group_vdbs = docTaskOptionsStore.data.group_vdbs;
  const lastUsedGVDBsID = current.previousQuery?.gvdbs_id || -999;
  useEffect(() => {
    if (waitingState) return;
    if (current.gvdbs_id === null) {
      const all_gvdbs_id = group_vdbs.map((row) => Number(row.gvdbs_id));
      const defaultGVDBsID = all_gvdbs_id.includes(lastUsedGVDBsID)
        ? lastUsedGVDBsID
        : Number(group_vdbs[0]?.gvdbs_id) || null;
      current.setGVDBsID(defaultGVDBsID);
    }
  }, [waitingState, current.gvdbs_id]);

  // update gvdbs_retr_params from group_vdbs row if necessary
  useEffect(() => {
    if (docTaskOptionsStore.needReload) return;
    if (!current.gvdbs_id || current.gvdbs_id === -1) return;
    const gvdbs_row = docTaskOptionsStore.gvdbs_id__row[current.gvdbs_id];
    const gvdbs_retr_params_str = gvdbs_row?.gvdbs_retr_params;
    if (gvdbs_retr_params_str) {
      defGVDBsRetrParamsStore.setData(gvdbs_retr_params_str);
      curGVDBsRetrParamsStore.copyFromDefault();
    }
    const gvdbs_retr_filters_str = gvdbs_row?.gvdbs_retr_filters;
    if (gvdbs_retr_filters_str) {
      defGVDBsRetrFiltersStore.setDataFromString(gvdbs_retr_filters_str);
    }
  }, [
    docTaskOptionsStore.needReload,
    defGVDBsRetrParamsStore.isLoaded,
    current.gvdbs_id,
  ]);

  function getSelectBgColor(gvdbs_id: number | null): string {
    if (waitingState || !gvdbs_id) return "";
    const row = docTaskOptionsStore.gvdbs_id__row[gvdbs_id];
    if (!row) return "#ECCCCF";
    if (row.gvdbs_status === "danger") return "#ECCCCF";
    if (row.gvdbs_status === "warning") return "#F2E7C3";
    return "";
  }

  function getOptionText(gvdbs_id: number | null): string {
    if (waitingState || !gvdbs_id) return "";
    const row = docTaskOptionsStore.gvdbs_id__row[gvdbs_id];
    if (!row) return "⛔ Not Found";
    if (row.gvdbs_status === "danger") return row.gvdbs_name + " ⛔";
    if (row.gvdbs_status === "warning") return row.gvdbs_name + " ⚠️";
    return row.gvdbs_name;
  }

  return (
    <InputGroup className="mb-2">
      <InputGroup.Text className="fw-bold bg-tc-300">
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
          //style={{ backgroundColor: getSelectBgColor(current.gvdbs_id) }}
        >
          {group_vdbs.map((gvdbs_obj) => (
            <option
              key={gvdbs_obj.gvdbs_id.toString()}
              value={gvdbs_obj.gvdbs_id.toString()}
              style={{ backgroundColor: getSelectBgColor(gvdbs_obj.gvdbs_id) }}
            >
              {getOptionText(gvdbs_obj.gvdbs_id)}
            </option>
          ))}
        </Form.Select>
      )}
      {user.is_superuser || user.is_groupadmin || user.is_contentmanager ? (
        <DocTasksGVDBsRetrParams></DocTasksGVDBsRetrParams>
      ) : null}
    </InputGroup>
  );
}
