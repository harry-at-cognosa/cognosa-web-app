import { useEffect } from "react";
import { Button, ListGroup } from "react-bootstrap";
import { useDocTasksShortStore } from "./useDocTasksShort";
import QueriesListBarItem from "./QueriesListBarItem";
import axiosClient from "../../../api/axiosClient";
import type { DocTasksShortQuery } from "../../../models/docTasksShortQuery";
import { useDocTasksCurrentStore } from "./useDocTasksCurrent";

function QueriesListBar() {
  const queriesStore = useDocTasksShortStore();
  const currentStore = useDocTasksCurrentStore();

  useEffect(() => {
    if (!queriesStore.needReload) return;
    async function fetchQueries() {
      try {
        const response = await axiosClient.post<DocTasksShortQuery>(
          "/doc_tasks/query_short"
        );
        const rows = response.data.rows;
        queriesStore.setRows(rows);
      } catch {
        alert("Error during fetching /doc_tasks/query_short");
      }
    }
    queriesStore.setNeedReload(false);
    fetchQueries();
  }, [queriesStore.needReload]);

  const todayRows = queriesStore.getTodayRows();
  const weekRows = queriesStore.getWeekRows();
  const beforeRows = queriesStore.getBeforeRows();

  return (
    <div className="w-100 bg-light border-end overflow-auto">
      <Button
        type="button"
        variant="light"
        className="w-100 fw-bold mt-2"
        style={{ backgroundColor: "var(--bs-gray-300)" }}
        onClick={() => currentStore.setNewQuery()}
      >
        New Query
      </Button>
      {todayRows.length ? (
        <>
          <h5 className="p-2 mb-0 bg-gray-100 bg-opacity-10">Today:</h5>
          <ListGroup as="ul" className="m-0">
            {todayRows.map((item) => (
              <QueriesListBarItem
                showDate={false}
                key={"recent_queries_" + item.doc_task_id}
                item={item}
              />
            ))}
          </ListGroup>
        </>
      ) : null}
      {weekRows.length ? (
        <>
          <h5 className="p-2 mb-0 bg-gray-100 bg-opacity-10">This week:</h5>
          <ListGroup as="ul" className="m-0">
            {weekRows.map((item) => (
              <QueriesListBarItem
                showDate={true}
                key={"recent_queries_" + item.doc_task_id}
                item={item}
              />
            ))}
          </ListGroup>
        </>
      ) : null}
      {beforeRows.length ? (
        <>
          <h5 className="p-2 mb-0 bg-gray-100 bg-opacity-10">Before:</h5>
          <ListGroup as="ul" className="m-0">
            {beforeRows.map((item) => (
              <QueriesListBarItem
                showDate={true}
                key={"recent_queries_" + item.doc_task_id}
                item={item}
              />
            ))}
          </ListGroup>
        </>
      ) : null}
    </div>
  );
}

export default QueriesListBar;
