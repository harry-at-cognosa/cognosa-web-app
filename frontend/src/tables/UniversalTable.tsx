import React, { useEffect } from "react";
import { Table, Spinner, Alert } from "react-bootstrap";
import type { createTableStore, TableRequest } from "./TableStoreFactory";

interface Props {
  endpoint: string;
  request: TableRequest;
  useStore: ReturnType<typeof createTableStore>;
}

const UniversalTable: React.FC<Props> = ({ endpoint, request, useStore }) => {
  const { loading, error, data, fetchTable } = useStore();

  useEffect(() => {
    fetchTable(endpoint, request);
  }, [endpoint, JSON.stringify(request)]);

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!data) return <p>No data</p>;
  const col_list: string[] = [];
  for (const col_name of Object.keys(data.columns)) col_list.push(col_name);

  return (
    <Table striped bordered hover responsive>
      <thead>
        <tr>
          {col_list.map((col) => (
            <th key={col}>{col}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.rows.map((row, idx) => (
          <tr key={row[data.pk] ?? idx}>
            {col_list.map((col) => (
              <td key={col}>{row[col]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default UniversalTable;
