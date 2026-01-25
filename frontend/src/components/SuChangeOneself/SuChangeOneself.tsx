import {
  Button,
  Dropdown,
  Form,
  InputGroup,
  Modal,
  Spinner,
} from "react-bootstrap";
import { useSuChangeOneselfStore } from "./useSuChangeOneselfStore";
import { useEffect, useState } from "react";
import { CheckCircleFill } from "react-bootstrap-icons";

export default function SuChangeOneself() {
  const [show, setShow] = useState(false);
  const store = useSuChangeOneselfStore();
  useEffect(() => {
    if (!store.needReload) return;
    async function fetchChangeOneselfData() {
      await store.fetchData();
    }
    fetchChangeOneselfData();
  }, [store.needReload]);
  useEffect(() => store.setNeedReload(true), []);

  const handleCancel = () => setShow(false);
  const handleApply = () => {
    store.setNeedReload(true);
    async function setOneself() {
      const result = await store.applyData();
      if (result?.is_success) {
        setShow(false);
        location.reload();
      }
    }
    setOneself();
  };
  return (
    <>
      <Dropdown.Item onClick={() => setShow(true)}>Change Group</Dropdown.Item>
      <Modal
        show={show}
        onHide={handleCancel}
        onShow={() => store.setNeedReload(true)}
      >
        <Modal.Header closeButton>
          <Modal.Title>Superuser: Group and Options</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {store.error_msg ? (
            <h3 style={{ color: "red" }}>{store.error_msg}</h3>
          ) : null}
          {store.firstLoad ? (
            <Spinner />
          ) : (
            <>
              <InputGroup className="mb-2">
                <InputGroup.Text
                  className="fw-bold justify-content-end bg-tc-300"
                  style={{ width: "17ch" }}
                >
                  Group:
                </InputGroup.Text>
                <Form.Select
                  className="fw-bold"
                  value={store.group_id}
                  autoComplete="off"
                  disabled={store.needReload}
                  onChange={(e) => {
                    store.setGroupId(Number(e.target.value));
                  }}
                >
                  {store.group_list.map((group) => (
                    <option key={group.group_id} value={group.group_id}>
                      {group.group_id}: {group.group_name}
                    </option>
                  ))}
                </Form.Select>
              </InputGroup>
              <InputGroup className="mb-2">
                <InputGroup.Text
                  className="fw-bold justify-content-end bg-tc-300"
                  style={{ width: "17ch" }}
                >
                  ContentManager:
                </InputGroup.Text>
                <Form.Select
                  className="fw-bold"
                  value={store.is_contentmanager ? 1 : 0}
                  autoComplete="off"
                  disabled={store.needReload}
                  onChange={(e) => {
                    store.setIsContentManager(Boolean(Number(e.target.value)));
                  }}
                >
                  <option key={"is_cm_yes"} value={1}>
                    Yes
                  </option>
                  <option key={"is_cm_no"} value={0}>
                    No
                  </option>
                </Form.Select>
              </InputGroup>
              <InputGroup className="mb-2">
                <InputGroup.Text
                  className="fw-bold justify-content-end bg-tc-300"
                  style={{ width: "17ch" }}
                >
                  GroupAdmin:
                </InputGroup.Text>
                <Form.Select
                  className="fw-bold"
                  value={store.is_groupadmin ? 1 : 0}
                  autoComplete="off"
                  disabled={store.needReload}
                  onChange={(e) => {
                    store.setIsGroupAdmin(Boolean(Number(e.target.value)));
                  }}
                >
                  <option key={"is_ga_yes"} value={1}>
                    Yes
                  </option>
                  <option key={"is_ga_no"} value={0}>
                    No
                  </option>
                </Form.Select>
              </InputGroup>
            </>
          )}
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
