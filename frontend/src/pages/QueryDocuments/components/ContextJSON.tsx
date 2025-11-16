import { Button, Card, Form, Modal } from "react-bootstrap";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useState } from "react";
import { useWebAppOptionsStore } from "../../../stores/useWebAppOptionsStore";

interface JsonItem {
  page_content: string;
  metadata: Record<string, any>;
  [key: string]: any; // Allow other properties
}

export default function ContextJSON() {
  const [isHovered, setIsHovered] = useState(false);
  const [show, setShow] = useState(false);
  const { context_json } = useDocTasksCurrentStore();
  const { color } = useWebAppOptionsStore();
  if (!context_json) return null;

  // Parse the JSON string
  let parsedData: JsonItem[] = [];
  try {
    parsedData = JSON.parse(context_json);
  } catch {}

  const headerText = "Found documents (" + parsedData.length + ")";
  function getItemHeader(item: JsonItem) {
    if (item?.metadata?.source)
      return (
        (item.metadata.source.length > 100 ? "..." : "") +
        item.metadata.source.slice(-100)
      );
    return item.page_content?.substring(0, 50) + "..." || "";
  }

  return (
    <>
      <Button
        type="button"
        className="me-2 fw-bold"
        size="sm"
        onClick={() => setShow(true)}
        style={{
          color: "black",
          backgroundColor: isHovered ? color.c400 : color.c300,
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {headerText + "..."}
      </Button>
      <Modal
        show={show}
        onHide={() => setShow(false)}
        size="xl"
        fullscreen="lg-down" // Fullscreen on small devices
      >
        <Modal.Header closeButton>
          <Modal.Title>{headerText + ":"}</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ maxHeight: "80vh", overflowY: "auto" }}>
          {parsedData.length === 0 ? (
            <div className="text-center py-4">
              <p>No data to display</p>
            </div>
          ) : (
            <div className="d-flex flex-column gap-4">
              {parsedData.map((item, index) => (
                <Card key={index} className="shadow-sm">
                  <Card.Header className="d-flex justify-content-between align-items-center">
                    <h6 className="mb-0">Item {index + 1}</h6>
                    <small className="text-muted">{getItemHeader(item)}</small>
                  </Card.Header>
                  <Card.Body>
                    <div className="row">
                      {/* Page Content - Textarea */}
                      <div className="col-md-6 mb-3 mb-md-0">
                        <Form.Group>
                          <Form.Label>
                            <strong>Page Content</strong>
                          </Form.Label>
                          <Form.Control
                            as="textarea"
                            rows={12} // Increased rows to match JSON display height
                            value={item.page_content || ""}
                            readOnly
                            style={{
                              fontFamily: "monospace",
                              fontSize: "12px",
                              resize: "vertical",
                              width: "100%",
                              height: "100%", // Ensure full height
                              minHeight: "300px", // Minimum height to match JSON area
                            }}
                          />
                        </Form.Group>
                      </div>

                      {/* Metadata and Other Fields - JSON */}
                      <div className="col-md-6">
                        <Card>
                          <Card.Header>
                            <strong>Metadata & Other Fields</strong>
                          </Card.Header>
                          <Card.Body className="p-0" style={{ height: "100%" }}>
                            <pre
                              className="mb-0"
                              style={{
                                backgroundColor: "#f8f9fa",
                                padding: "1rem",
                                margin: 0,
                                height: "calc(100% - 2rem)", // Full height minus padding
                                maxHeight: "none",
                                overflow: "auto",
                                fontFamily: "monospace",
                                fontSize: "12px",
                                borderRadius: "0 0 4px 4px",
                                whiteSpace: "pre-wrap",
                                wordBreak: "break-word",
                              }}
                            >
                              {JSON.stringify(
                                {
                                  metadata: item.metadata,
                                  ...Object.fromEntries(
                                    Object.entries(item).filter(
                                      ([key]) => key !== "page_content"
                                    )
                                  ),
                                },
                                null,
                                2
                              )}
                            </pre>
                          </Card.Body>
                        </Card>
                      </div>
                    </div>
                  </Card.Body>
                </Card>
              ))}
            </div>
          )}
        </Modal.Body>
      </Modal>
    </>
  );
}
