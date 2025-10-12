import { useEffect } from "react";
import { Table, Spinner, Alert, Button } from "react-bootstrap";
import type { createTableStore } from "./TableStoreFactory";
import ColumnDisplayName from "./elements/ColumnDisplayName";
import ViewCellElement from "./elements/ViewCellElement";
import AskDelete from "./elements/AskDelete";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function UniversalTable({ useStore }: Props) {
  const tableStore = useStore();
  const { data } = tableStore;

  useEffect(() => {
    if (!tableStore.needReload) return;
    tableStore.queryTable();
  }, [tableStore.needReload]);
  useEffect(() => tableStore.setNeedReload(true), []);

  if (tableStore.loading) return <Spinner animation="border" />;
  if (tableStore.error)
    return <Alert variant="danger">{tableStore.error}</Alert>;
  if (!data) return <p>No data</p>;

  return (
    <>
      <Table striped bordered hover responsive>
        <thead>
          <tr style={{ textAlign: "center", verticalAlign: "middle" }}>
            {/* edit th */}
            {data.table_options.update__allow ? <th></th> : null}
            {/* visible columns display names */}
            {tableStore.visible_columns.map((col) => (
              <th key={col} className="text-nowrap">
                <ColumnDisplayName data={data} col={col}></ColumnDisplayName>
              </th>
            ))}
            {/* delete th */}
            {data.table_options.delete__allow ? <th></th> : null}
          </tr>
        </thead>
        <tbody>
          {data.rows.map((row) => (
            <tr
              key={row[data.table_options.pk]?.toString()}
              style={{ textAlign: "center", verticalAlign: "middle" }}
            >
              {/* edit button cell */}
              {data.table_options.update__allow ? (
                <td>
                  <Button type="button" variant="secondary">
                    Edit
                  </Button>
                </td>
              ) : null}
              {/* visible columns */}
              {tableStore.visible_columns.map((col) => (
                <td key={col}>
                  <ViewCellElement
                    data={data}
                    row={row}
                    col={col}
                  ></ViewCellElement>
                </td>
              ))}
              {/* delete button cell */}
              {data.table_options.delete__allow ? (
                <td>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => tableStore.setAskDelete(row)}
                  >
                    X
                  </Button>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </Table>
      <AskDelete useStore={useStore}></AskDelete>
    </>
  );
}
