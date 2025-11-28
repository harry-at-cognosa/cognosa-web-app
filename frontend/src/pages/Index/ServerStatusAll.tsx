import { Card, Table } from "react-bootstrap";
import {
  useServerStatusStore,
  type ServerStatusResponse,
} from "./useServerStatusStore";
import { useEffect } from "react";
import axiosClient from "../../api/axiosClient";

async function fetchBackendData() {
  try {
    const { data } = await axiosClient.get<ServerStatusResponse>(
      "/server_status"
    );
    useServerStatusStore.getState().setData(data);
    return data;
  } catch (err) {
    console.error("Failed to fetch backend data:", err);
    throw err;
  }
}

export default function ServerStatusAll() {
  const { api_settings, group_vdbs_rows, group_llms_rows } =
    useServerStatusStore();
  useEffect(() => {
    fetchBackendData();
    const interval = setInterval(() => {
      fetchBackendData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const textAppVersion = `App version: ${api_settings.app_version}`;
  const textDBVersion = `Database version: ${api_settings.db_version}`;

  return (
    <>
      {/* App/DB versions*/}
      <div className="m-3 d-flex justify-content-center">
        <div className="text-center mb-0 fw-bold" key={"app_db_versions"}>
          <span className="me-3">{textAppVersion}</span>
          <span>{textDBVersion}</span>
        </div>
      </div>
      <Card className="rounded-3 shadow-sm mb-4">
        <Card.Header className="fw-bold bg-tc-300">
          Vector Databases and Collections:
        </Card.Header>
        <Card.Body className="p-0">
          <Table className="mb-0" striped hover size="sm">
            <tbody>
              {group_vdbs_rows.map((vdb, idx) => (
                <tr key={idx} className={"table-" + vdb.gvdbs_status}>
                  <td style={{ width: "50%", textAlign: "center" }}>
                    {vdb.gvdbs_name}
                  </td>
                  <td>{vdb.gvdbs_status_text}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
      <Card className="rounded-3 shadow-sm mb-3">
        <Card.Header className="fw-bold bg-tc-300">Available LLM:</Card.Header>
        <Card.Body className="p-0">
          <Table className="mb-0" striped hover size="sm">
            <tbody>
              {group_llms_rows.map((llm, idx) => (
                <tr key={idx} className={"table-" + llm.gllms_status}>
                  <td style={{ width: "50%", textAlign: "center" }}>
                    {llm.gllms_name}
                  </td>
                  <td>{llm.gllms_status_text}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </>
  );
}
