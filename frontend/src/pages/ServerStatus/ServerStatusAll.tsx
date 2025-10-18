import { Col, Container, Row, Table } from "react-bootstrap";
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

function ServerStatusAll() {
  const { api_settings, run_tasks, group_vdbs_rows, group_llms_rows } =
    useServerStatusStore();
  useEffect(() => {
    fetchBackendData();
    const interval = setInterval(() => {
      fetchBackendData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const textAppDBVersions = `APP: ${api_settings.app_version} DB: ${api_settings.db_version}`;

  return (
    <Container className="py-3">
      <Row className="gy-4">
        {/* App/DB versions*/}
        <Col className="text-center mb-0" xs={12} key={"app_db_versions"}>
          <h4>{textAppDBVersions}</h4>
        </Col>

        {/* Run Tasks Tables */}
        {run_tasks.map((task) => (
          <Col xs={12} key={task.name}>
            <h4>{task.name}</h4>
            <Table bordered hover size="sm">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {task.subprocesses.map((sp) => (
                  <tr key={sp.name} className={"table-" + sp.is_good}>
                    <td>{sp.name}</td>
                    <td>{sp.status_text}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Col>
        ))}

        {/* GroupVBDs Table */}
        <Col xs={12}>
          <h4>GroupVDBs</h4>
          <Table striped bordered hover size="sm">
            <thead>
              <tr>
                <th>Group ID</th>
                <th>Seqn #</th>
                <th>Type</th>
                <th>Name</th>
                <th>URL</th>
                <th>Collection</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {group_vdbs_rows.map((vdb, idx) => (
                <tr key={idx} className={"table-" + vdb.gvdbs_status}>
                  <td>{vdb.group_id}</td>
                  <td>{vdb.gvdbs_seqn}</td>
                  <td>{vdb.gvdbs_type}</td>
                  <td>{vdb.gvdbs_name}</td>
                  <td>{vdb.gvdbs_url}</td>
                  <td>{vdb.gvdbs_collection}</td>
                  <td>{vdb.gvdbs_status_text}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Col>

        {/* GroupLLMs Table */}
        <Col xs={12}>
          <h4>GroupLLMs</h4>
          <Table striped bordered hover size="sm">
            <thead>
              <tr>
                <th>Group ID</th>
                <th>Seqn #</th>
                <th>Type</th>
                <th>Name</th>
                <th>API BASE</th>
                <th>Model</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {group_llms_rows.map((llm, idx) => (
                <tr key={idx} className={"table-" + llm.gllms_status}>
                  <td>{llm.group_id}</td>
                  <td>{llm.gllms_seqn}</td>
                  <td>{llm.gllms_type}</td>
                  <td>{llm.gllms_name}</td>
                  <td>{llm.gllms_api_base}</td>
                  <td>{llm.gllms_model}</td>
                  <td>{llm.gllms_status_text}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Col>
      </Row>
    </Container>
  );
}

export default ServerStatusAll;
