import { useState } from "react";
import { Button, Container, Modal } from "react-bootstrap";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { ArrowRepeat, CheckCircleFill, GearFill } from "react-bootstrap-icons";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useDefaultGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useDefaultGVDBsRetrFiltersStore";
import { useModalGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useModalGVDBsRetrFiltersStore";
import GVDBsRetrFilters from "../../../components/GVDBsRetrFilters/GVDBsRetrFilters";
import { useDocTasksGVDBsRetrFiltersStore } from "../../../components/GVDBsRetrFilters/useDocTasksGVDBsRetrFiltersStore";
import GVDBsRetrFiltersTable from "../../../components/GVDBsRetrFilters/GVDBsRetrFiltersTable";
import { GVDBsRetrFiltersHistory } from "../../../components/GVDBsRetrFilters/history";

export default function DocTasksGVDBsRetrFilters() {
  const { doc_task_id, gvdbs_id } = useDocTasksCurrentStore();
  const DocTaskOptionsStore = useDocTaskOptionsStore();
  const [show, setShow] = useState(false);
  const defStore = useDefaultGVDBsRetrFiltersStore();
  const modalStore = useModalGVDBsRetrFiltersStore();
  const curStore = useDocTasksGVDBsRetrFiltersStore();

  if (DocTaskOptionsStore.needReload) return null;
  if (!(defStore.isLoaded && defStore.fields)) return null;
  if (gvdbs_id === -1) return null;

  const handleCancel = () => {
    setShow(false);
    modalStore.reset();
  };
  const handleApply = () => {
    setShow(false);
    const global_not_enabled = defStore.global_not_enabled || false;
    const fields = defStore.fields || [];
    GVDBsRetrFiltersHistory.update(
      doc_task_id,
      gvdbs_id,
      modalStore.global_not_value,
      modalStore.rf_field_id__values,
    );
    curStore.initData(
      { global_not_enabled, fields },
      modalStore.global_not_value,
      modalStore.rf_field_id__values,
    );
    modalStore.reset();
  };
  const handleShow = () => {
    if (show) return;
    // modal will show default values + current DocTask values.
    const {
      isLoaded: defLoaded,
      global_not_enabled: defGlobalNotEnabled,
      fields: defFields,
    } = defStore;
    if (!(defLoaded && defFields && defGlobalNotEnabled !== null)) return;

    modalStore.initData(
      {
        global_not_enabled: defGlobalNotEnabled,
        fields: defFields,
      },
      curStore.global_not_value,
      curStore.rf_field_id__values,
    );
    setShow(true);
  };

  return (
    <Container fluid className="mb-2 p-0">
      <Button
        variant="outline-secondary"
        className="fw-bold btn-tc-300-400"
        style={{
          color: "black",
        }}
        onClick={handleShow}
      >
        <GearFill size={"20px"} style={{ marginBottom: "2px" }}></GearFill>
        &nbsp;
        {"Retrieval Filters "}
      </Button>
      <Button
        variant="outline-secondary"
        className="fw-bold ms-2 btn-tc-300-400"
        style={{
          color: "black",
        }}
        onClick={() => {
          curStore.reset();
        }}
      >
        <ArrowRepeat size="20px" style={{ marginBottom: "3px" }} /> Reset
      </Button>

      <Modal show={show} onHide={handleCancel}>
        <Modal.Header closeButton>
          <Modal.Title>Retrieval Filters</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <GVDBsRetrFilters />
        </Modal.Body>
        <Modal.Footer className="justify-content-center">
          <Button
            variant="success"
            className="fw-bold btn-tc-300-400"
            onClick={handleApply}
            style={{ color: "black" }}
          >
            <CheckCircleFill
              className="me-1 my-0"
              size="20px"
              style={{ color: "green" }}
            ></CheckCircleFill>
            Apply
          </Button>
        </Modal.Footer>
      </Modal>
      <GVDBsRetrFiltersTable />
    </Container>
  );
}
