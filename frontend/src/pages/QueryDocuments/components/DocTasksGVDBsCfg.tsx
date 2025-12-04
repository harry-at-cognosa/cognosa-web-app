import { useState } from "react";
import { Button, Modal } from "react-bootstrap";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { CheckCircleFill, GearFill } from "react-bootstrap-icons";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import {
  useDocTasksGVDBsCfgStore,
  useTempGVDBsCfgStore,
} from "../../../components/GVDBsCfg/stores";
import getGVDBsCfgShortName from "../../../components/GVDBsCfg/GVDBsCfgShortName";
import GVDBsCfg from "../../../components/GVDBsCfg/GVDBsCfg";

export default function DocTasksGVDBsCfg() {
  const current = useDocTasksCurrentStore();
  const DocTaskOptionsStore = useDocTaskOptionsStore();
  const cfgStore = useDocTasksGVDBsCfgStore();
  const [show, setShow] = useState(false);
  const tempStore = useTempGVDBsCfgStore();

  if (DocTaskOptionsStore.needReload) return null;

  const handleCancel = () => setShow(false);
  const handleApply = () => {
    cfgStore.setSearchType(tempStore.search_type);
    cfgStore.setSearchKwargs({ ...tempStore.search_kwargs });
    setShow(false);
  };
  const handleShow = () => {
    tempStore.setSearchType(cfgStore.search_type);
    tempStore.setSearchKwargs(cfgStore.search_kwargs);
    setShow(true);
  };

  return (
    <>
      <Button
        variant="outline-secondary"
        className="fw-bold btn-tc-300-400"
        style={{
          color: "black",
        }}
        onClick={handleShow}
        disabled={current.gvdbs_id === -1}
      >
        <GearFill size={"20px"}></GearFill>&nbsp;
        {getGVDBsCfgShortName({ cfgStore })}
      </Button>

      <Modal show={show} onHide={handleCancel}>
        <Modal.Header closeButton>
          <Modal.Title>VDB Search Options</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <GVDBsCfg tempStore={tempStore} />
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
    </>
  );
}
