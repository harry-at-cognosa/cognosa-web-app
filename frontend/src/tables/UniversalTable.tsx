import { useEffect } from "react";
import { Table, Spinner, Alert, Button } from "react-bootstrap";
import type { createTableStore } from "./TableStoreFactory";
import OnlyEnableCheck from "./CellRenders/OnlyEnableCheck";
import TextCell from "./CellRenders/TextCell";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function UniversalTable({ useStore }: Props) {
  const {
    loading,
    error,
    data,
    visible_columns,
    needReload,
    setNeedReload,
    queryTable,
  } = useStore();

  useEffect(() => {
    if (!needReload) return;
    queryTable();
  }, [needReload]);
  useEffect(() => setNeedReload(true), []);

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!data) return <p>No data</p>;
  const { rows, columns } = data;

  function getDisplayName(col: string) {
    let displayName = columns[col].display || col;
    let lines = displayName.split("\n");
    if (lines.length > 1) return lines.map((x) => <div>{x}</div>);
    return displayName;
  }

  function getCellElement(row: Record<string, any>, col: string) {
    if (!data) return null;
    const value = row[col];
    const cellType = data.columns[col].type;
    if (cellType === "bool_green")
      return <OnlyEnableCheck value={value}></OnlyEnableCheck>;
    if (cellType === "text") return <TextCell value={value}></TextCell>;
    return value.toString();
  }

  return (
    <Table striped bordered hover responsive>
      <thead>
        <tr style={{ textAlign: "center", verticalAlign: "middle" }}>
          {/* edit th */}
          {data.table_options.allow_update ? <th></th> : null}
          {/* visible columns display names */}
          {visible_columns.map((col) => (
            <th key={col} className="text-nowrap">
              {getDisplayName(col)}
            </th>
          ))}
          {/* delete th */}
          {data.table_options.allow_delete ? <th></th> : null}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr
            key={row[data.table_options.pk]}
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            {/* edit button cell */}
            {data.table_options.allow_update ? (
              <td>
                <Button type="button" variant="secondary">
                  Edit
                </Button>
              </td>
            ) : null}
            {/* visible columns */}
            {visible_columns.map((col) => (
              <td key={col}>{getCellElement(row, col)}</td>
            ))}
            {/* delete button cell */}
            {data.table_options.allow_delete ? (
              <td>
                <Button type="button" variant="secondary">
                  X
                </Button>
              </td>
            ) : null}
          </tr>
        ))}
      </tbody>
    </Table>
  );
}
