import { useState } from "react";
import { Button, Modal, Tabs, Tab, Form, Row, Col } from "react-bootstrap";
import { useDocTasksGVDBsCfgStore } from "../stores/useDocTasksGVDBsCfg";
import { useWebAppOptionsStore } from "../../../stores/useWebAppOptionsStore";
import { useDocTaskOptionsStore } from "../stores/useDocTaskOptionsStore";

export default function DocTasksGVDBsCfg() {
  const DocTaskOptionsStore = useDocTaskOptionsStore();
  const { color } = useWebAppOptionsStore();
  const { search_type, search_kwargs, setSearchType, setKwargsField } =
    useDocTasksGVDBsCfgStore();
  const [show, setShow] = useState(false);

  if (DocTaskOptionsStore.needReload) return null;

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  const handleKChange = (value: string) => {
    const num = value === "" ? undefined : parseInt(value, 10);
    setKwargsField("k", isNaN(num as number) ? undefined : num);
  };

  const handleFetchKChange = (value: string) => {
    const num = value === "" ? undefined : parseInt(value, 10);
    setKwargsField("fetch_k", isNaN(num as number) ? undefined : num);
  };

  const handleLambdaChange = (value: string) => {
    const num = value === "" ? undefined : parseFloat(value);
    setKwargsField("lambda_mult", isNaN(num as number) ? undefined : num);
  };

  const handleScoreThresholdChange = (value: string) => {
    const num = value === "" ? undefined : parseFloat(value);
    setKwargsField("score_threshold", isNaN(num as number) ? undefined : num);
  };

  return (
    <>
      <Button
        variant="outline-secondary"
        className="fw-bold"
        style={{
          color: "black",
          backgroundColor: color.c300,
          borderColor: color.c300,
        }}
        onClick={handleShow}
      >
        Search Options...
      </Button>

      <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>VDB Search Options</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Tabs
            activeKey={search_type}
            onSelect={(key) => key && setSearchType(key as any)}
            className="mb-3"
          >
            <Tab eventKey="similarity" title="Similarity">
              <Row className="mb-2">
                <Col>
                  <Form.Group>
                    <Form.Label>k</Form.Label>
                    <Form.Control
                      type="number"
                      value={search_kwargs.k ?? "10"}
                      onChange={(e) => handleKChange(e.target.value)}
                      min={1}
                    />
                  </Form.Group>
                </Col>
              </Row>
            </Tab>

            <Tab eventKey="mmr" title="MMR">
              <Row className="mb-2">
                <Col>
                  <Form.Group>
                    <Form.Label>k</Form.Label>
                    <Form.Control
                      type="number"
                      value={search_kwargs.k ?? "10"}
                      onChange={(e) => handleKChange(e.target.value)}
                      min={1}
                    />
                  </Form.Group>
                </Col>
              </Row>
              <Row className="mb-2">
                <Col>
                  <Form.Group>
                    <Form.Label>fetch_k</Form.Label>
                    <Form.Control
                      type="number"
                      value={search_kwargs.fetch_k ?? "20"}
                      onChange={(e) => handleFetchKChange(e.target.value)}
                      min={1}
                    />
                  </Form.Group>
                </Col>
              </Row>
              <Row className="mb-2">
                <Col>
                  <Form.Group>
                    <Form.Label>lambda_mult</Form.Label>
                    <Form.Control
                      type="number"
                      step="0.01"
                      value={search_kwargs.lambda_mult ?? "0.5"}
                      onChange={(e) => handleLambdaChange(e.target.value)}
                      min={0}
                      max={1}
                    />
                  </Form.Group>
                </Col>
              </Row>
            </Tab>

            <Tab eventKey="similarity_score_threshold" title="Score Threshold">
              <Row className="mb-2">
                <Col>
                  <Form.Group>
                    <Form.Label>k</Form.Label>
                    <Form.Control
                      type="number"
                      value={search_kwargs.k ?? "10"}
                      onChange={(e) => handleKChange(e.target.value)}
                      min={1}
                    />
                  </Form.Group>
                </Col>
              </Row>
              <Row className="mb-2">
                <Col>
                  <Form.Group>
                    <Form.Label>score_threshold</Form.Label>
                    <Form.Control
                      type="number"
                      step="0.01"
                      value={search_kwargs.score_threshold ?? "0.5"}
                      onChange={(e) =>
                        handleScoreThresholdChange(e.target.value)
                      }
                      min={0}
                      max={1}
                    />
                  </Form.Group>
                </Col>
              </Row>
            </Tab>
          </Tabs>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            OK
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
