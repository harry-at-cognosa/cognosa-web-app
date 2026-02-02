import { useState } from "react";
import { Button, Modal } from "react-bootstrap";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { ArrowRepeat, CheckCircleFill, GearFill } from "react-bootstrap-icons";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import GVDBsRetrParams from "../../../components/GVDBsRetrParams/GVDBsRetrParams";
import { useDefaultGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useDefaultGVDBsRetrParamsStore";
import { useModalGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useModalGVDBsRetrParamsStore";
import { useDocTasksGVDBsRetrParamsStore } from "../../../components/GVDBsRetrParams/useDocTasksGVDBsRetrParamsStore";

export default function DocTasksGVDBsRetrParams() {
  const { gvdbs_id } = useDocTasksCurrentStore();
  const DocTaskOptionsStore = useDocTaskOptionsStore();
  const [show, setShow] = useState(false);
  const modalStore = useModalGVDBsRetrParamsStore();
  const defStore = useDefaultGVDBsRetrParamsStore();
  const curStore = useDocTasksGVDBsRetrParamsStore();

  if (DocTaskOptionsStore.needReload) return null;
  if (!defStore.isLoaded) return null;

  const modalDisabled = gvdbs_id === -1;

  const handleCancel = () => setShow(false);
  const handleApply = () => {
    const {
      search_type,
      search_kwargs__similarity,
      search_kwargs__mmr,
      search_kwargs__similarity_score_threshold,
    } = modalStore;
    if (
      !(
        search_type &&
        search_kwargs__similarity &&
        search_kwargs__mmr &&
        search_kwargs__similarity_score_threshold
      )
    )
      return;
    curStore.setData({
      search_type,
      search_kwargs__similarity: { ...search_kwargs__similarity },
      search_kwargs__mmr: { ...search_kwargs__mmr },
      search_kwargs__similarity_score_threshold: {
        ...search_kwargs__similarity_score_threshold,
      },
    });
    setShow(false);
  };
  const handleShow = () => {
    // modal will show default values + current DocTask values.
    const {
      isLoaded: defLoaded,
      search_type: defSearchType,
      search_kwargs__similarity: defSkSIM,
      search_kwargs__mmr: defSkMMR,
      search_kwargs__similarity_score_threshold: defSkSST,
    } = defStore;
    if (!(defLoaded && defSearchType && defSkSIM && defSkMMR && defSkSST))
      return;
    let newData = {
      search_type: defSearchType,
      search_kwargs__similarity: { ...defSkSIM },
      search_kwargs__mmr: { ...defSkMMR },
      search_kwargs__similarity_score_threshold: { ...defSkSST },
    };
    const {
      isLoaded: curLoaded,
      search_type: curSearchType,
      search_kwargs__similarity: curSkSIM,
      search_kwargs__mmr: curSkMMR,
      search_kwargs__similarity_score_threshold: curSkSST,
    } = curStore;
    if (curLoaded && curSearchType && curSkSIM && curSkMMR && curSkSST) {
      newData.search_type = curSearchType;
      if (curSearchType === "similarity")
        newData.search_kwargs__similarity = { ...curSkSIM };
      if (curSearchType === "mmr") newData.search_kwargs__mmr = { ...curSkMMR };
      if (curSearchType === "similarity_score_threshold")
        newData.search_kwargs__similarity_score_threshold = { ...curSkSST };
    }
    modalStore.setData(newData);

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
        disabled={modalDisabled}
      >
        <GearFill size={"20px"} style={{ marginBottom: "2px" }}></GearFill>
        &nbsp;
        {"Retrieval Parameters: " +
          (modalDisabled ? "N/A" : curStore.getShortName())}
      </Button>
      <Button
        variant="outline-secondary"
        className="fw-bold btn-tc-300-400"
        style={{
          color: "black",
        }}
        onClick={() => {
          curStore.copyFromDefault();
        }}
        disabled={modalDisabled}
      >
        <ArrowRepeat size="20px" style={{ marginBottom: "3px" }} /> Reset
      </Button>

      <Modal show={show} onHide={handleCancel}>
        <Modal.Header closeButton>
          <Modal.Title>VDB Retrieval Parameters</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <GVDBsRetrParams />
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
