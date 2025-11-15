import { Modal, Spinner } from "react-bootstrap";
import type { createTableStore } from "../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function BusyModal({ useStore }: Props) {
  const { busy } = useStore();
  if (busy !== "create_pending" && busy !== "update_pending") return null;
  return (
    <Modal
      show={true}
      backdrop="static"
      keyboard={false}
      style={{ zIndex: 2000 }}
      centered
    >
      <Modal.Body className="text-center p-4">
        <Spinner animation="border" className="mb-3" />
        <div className="fw-bold">Processing, please wait...</div>
      </Modal.Body>
    </Modal>
  );
}
