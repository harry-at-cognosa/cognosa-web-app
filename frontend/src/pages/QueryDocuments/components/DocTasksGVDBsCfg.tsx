import { useState } from "react";
import { Button, Modal, Form, InputGroup } from "react-bootstrap";
import {
  useDocTasksGVDBsCfgStore,
  useModalGVDBsCfgStore,
  type SearchType,
} from "../stores/useDocTasksGVDBsCfg";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";
import { CheckCircleFill, GearFill } from "react-bootstrap-icons";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import clsx from "clsx";

export default function DocTasksGVDBsCfg() {
  const current = useDocTasksCurrentStore();
  const DocTaskOptionsStore = useDocTaskOptionsStore();
  const cfgStore = useDocTasksGVDBsCfgStore();
  const [show, setShow] = useState(false);
  const modalStore = useModalGVDBsCfgStore();

  if (DocTaskOptionsStore.needReload) return null;

  const handleCancel = () => setShow(false);
  const handleApply = () => {
    cfgStore.setSearchType(modalStore.search_type);
    cfgStore.setSearchKwargs({ ...modalStore.search_kwargs });
    setShow(false);
  };
  const handleShow = () => {
    modalStore.setSearchType(cfgStore.search_type);
    modalStore.setSearchKwargs(cfgStore.search_kwargs);
    setShow(true);
  };

  const handleKandFetchKChange = (name: "k" | "fetch_k", value: string) => {
    let value_int = parseInt(value, 10);
    if (isNaN(value_int)) return;
    if (value_int <= 0) value_int = 1;
    modalStore.setKwargsField(name, value_int);
  };

  const handleLMandSTChange = (
    name: "lambda_mult" | "score_threshold",
    value: string
  ) => {
    let value_float = Number(value);
    if (isNaN(value_float)) return;
    if (value_float < 0) value_float = 0;
    if (value_float > 1) value_float = 1;
    modalStore.setKwargsField(name, value_float);
  };

  const disabledFetchK = modalStore.search_type !== "mmr";
  const disabledLambdaMult = modalStore.search_type !== "mmr";
  const disabledScoreThreshold =
    modalStore.search_type !== "similarity_score_threshold";

  function getModalOpenButtonText() {
    let text = "Search Options: ";
    const { k, fetch_k, lambda_mult, score_threshold } = cfgStore.search_kwargs;
    if (cfgStore.search_type === "similarity") {
      text += "SIM: " + k;
    } else if (cfgStore.search_type === "mmr") {
      text += "MMR: " + k + "/" + fetch_k + "/" + lambda_mult;
    } else if (cfgStore.search_type === "similarity_score_threshold") {
      text += "SST: " + k + "/" + score_threshold;
    }
    return text;
  }
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
        {getModalOpenButtonText()}
      </Button>

      <Modal show={show} onHide={handleCancel}>
        <Modal.Header closeButton>
          <Modal.Title>VDB Search Options</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <InputGroup className="mb-2">
            <InputGroup.Text
              className="fw-bold justify-content-end bg-tc-300"
              style={{ width: "16ch" }}
            >
              Search Type:
            </InputGroup.Text>
            <Form.Select
              className="fw-bold"
              value={modalStore.search_type}
              onChange={(e) =>
                modalStore.setSearchType(e.target.value as SearchType)
              }
              autoComplete="off"
            >
              {modalStore.search_type_name.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </Form.Select>
          </InputGroup>
          <hr />
          <InputGroup className="mb-2">
            <InputGroup.Text
              className="fw-bold justify-content-end bg-tc-300"
              style={{ width: "16ch" }}
            >
              k:
            </InputGroup.Text>
            <Form.Control
              type="number"
              className="fw-bold"
              value={modalStore.search_kwargs.k}
              onChange={(e) => handleKandFetchKChange("k", e.target.value)}
              min={1}
            />
          </InputGroup>
          <InputGroup className="mb-2">
            <InputGroup.Text
              className={clsx(
                "fw-bold justify-content-end",
                disabledFetchK ? "bg-tc-100" : "bg-tc-300"
              )}
              style={{ width: "16ch" }}
            >
              fetch_k:
            </InputGroup.Text>
            <Form.Control
              type="number"
              className="fw-bold"
              value={modalStore.search_kwargs.fetch_k}
              disabled={disabledFetchK}
              onChange={(e) =>
                handleKandFetchKChange("fetch_k", e.target.value)
              }
              min={1}
            />
          </InputGroup>
          <InputGroup className="mb-2">
            <InputGroup.Text
              className={clsx(
                "fw-bold justify-content-end",
                disabledLambdaMult ? "bg-tc-100" : "bg-tc-300"
              )}
              style={{ width: "16ch" }}
            >
              lambda_mult:
            </InputGroup.Text>
            <Form.Control
              type="number"
              step="0.01"
              className="fw-bold"
              disabled={disabledLambdaMult}
              value={modalStore.search_kwargs.lambda_mult}
              onChange={(e) =>
                handleLMandSTChange("lambda_mult", e.target.value)
              }
              min={0}
              max={1}
            />
          </InputGroup>
          <InputGroup className="mb-2">
            <InputGroup.Text
              className={clsx(
                "fw-bold justify-content-end",
                disabledScoreThreshold ? "bg-tc-100" : "bg-tc-300"
              )}
              style={{ width: "16ch" }}
            >
              score_threshold:
            </InputGroup.Text>
            <Form.Control
              type="number"
              step="0.01"
              className="fw-bold"
              disabled={disabledScoreThreshold}
              value={modalStore.search_kwargs.score_threshold}
              onChange={(e) =>
                handleLMandSTChange("score_threshold", e.target.value)
              }
              min={0}
              max={1}
            />
          </InputGroup>
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
