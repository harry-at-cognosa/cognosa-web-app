import { useEffect } from "react";
import axiosClient from "../../../api/axiosClient";
import type { DocTasksShortQuery } from "../models/docTasksShortQuery";
import { useDocTasksShortStore } from "../stores/useDocTasksShort";
import { useQueryNotice } from "./useQueryNotice";

/**
 * Loads the short list of queries. Mounted by the page, not by the list, so
 * the list is kept up to date while it is collapsed or (on a phone) closed.
 */
export function useQueriesListLoader() {
  const queriesStore = useDocTasksShortStore();
  useEffect(() => {
    if (!queriesStore.needReload) return;
    async function fetchQueries() {
      try {
        const response = await axiosClient.post<DocTasksShortQuery>(
          "/doc_tasks/query_short",
        );
        const rows = response.data.rows;
        queriesStore.setRows(rows);
      } catch {
        useQueryNotice
          .getState()
          .show("Error during fetching /doc_tasks/query_short");
      }
    }
    queriesStore.setNeedReload(false);
    fetchQueries();
  }, [queriesStore.needReload]);
}
