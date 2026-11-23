import { useState } from "react";
import { ConfirmDelete } from "@/components/ConfirmDelete";
import { GroupLabel } from "@/components/SplitLayout";
import { useDocTasksShortStore } from "../stores/useDocTasksShort";
import QueriesListBarItem from "./QueriesListBarItem";
import axiosClient from "../../../api/axiosClient";
import type { DocTasksShortItem } from "../models/docTasksShortItem";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useQueryDocumentsStore } from "../stores/useQueryDocumentStore";
import { useQueryNotice } from "../hooks/useQueryNotice";

interface Props {
  /** called after a query was chosen (closes the list on a phone) */
  afterPick?: () => void;
}

function QueriesListBar({ afterPick }: Props) {
  const queryStore = useQueryDocumentsStore();
  const queriesStore = useDocTasksShortStore();
  const currentStore = useDocTasksCurrentStore();
  const [pending, setPending] = useState<DocTasksShortItem | null>(null);

  const handleDelete = async (doc_task_id: number) => {
    try {
      await axiosClient.delete(`/doc_tasks/${doc_task_id}`);
      queriesStore.deleteRow(doc_task_id);
    } catch (error) {
      console.error("Failed to delete query:", error);
      useQueryNotice.getState().show("Failed to delete query. Please try again.");
    } finally {
      if (doc_task_id === useDocTasksCurrentStore.getState().doc_task_id) {
        // clear query if it was current
        queryStore.setOpUUID("");
        queryStore.stopPolling();
        currentStore.cloneQuery();
      }
    }
  };

  const groups: [string, boolean, DocTasksShortItem[]][] = [
    ["Today", false, queriesStore.getTodayRows()],
    ["This week", true, queriesStore.getWeekRows()],
    ["Before", true, queriesStore.getBeforeRows()],
  ];

  return (
    <>
      <ConfirmDelete
        name={pending ? pending.short_name : null}
        onCancel={() => setPending(null)}
        onConfirm={() => {
          if (pending) handleDelete(pending.doc_task_id);
          setPending(null);
        }}
      />
      {groups.map(([label, showDate, rows]) =>
        rows.length ? (
          <div key={label}>
            <GroupLabel>{label}</GroupLabel>
            <ul>
              {rows.map((item) => (
                <QueriesListBarItem
                  showDate={showDate}
                  key={"recent_queries_" + item.doc_task_id}
                  item={item}
                  onDelete={setPending}
                  afterPick={afterPick}
                />
              ))}
            </ul>
          </div>
        ) : null,
      )}
    </>
  );
}

export default QueriesListBar;
