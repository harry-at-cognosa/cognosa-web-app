import { Spinner } from "react-bootstrap";

export default function CenteredSpinner() {
  return (
    <div
      className="d-flex justify-content-center align-items-center"
      style={{ minHeight: "100vh" }}
    >
      <Spinner animation="border" role="status" />
    </div>
  );
}
