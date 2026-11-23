import { useEffect } from "react";
import { PageHead } from "@/components/Shell";
import { SplitLayout } from "@/components/SplitLayout";
import QueriesListBar from "./components/QueriesListBar";
import { useQueriesListLoader } from "./hooks/useQueriesListLoader";
import QueryArea from "./components/QueryArea";
import ResponseArea from "./components/ResponseArea";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import { useDocTaskOptionsStore } from "./stores/useDocTaskOptionsStore";
import { useDocTasksCurrentStore } from "./stores/useDocTasksCurrent";
import { useQueryDocumentsStore } from "./stores/useQueryDocumentStore";
import { useQueryNotice } from "./hooks/useQueryNotice";
import { useAsked } from "./hooks/useAskedQuestion";
import CenteredSpinner from "../../components/CenteredSpinner";

export default function QueryDocumentsPage() {
  useTopNavBarTitle("Query Documents");
  const docTaskOptionsStore = useDocTaskOptionsStore();
  useQueriesListLoader();

  useEffect(() => {
    if (!docTaskOptionsStore.needReload) return;
    async function fetchDocTaskOptions() {
      await docTaskOptionsStore.fetchData();
    }
    fetchDocTaskOptions();
  }, [docTaskOptionsStore.needReload]);
  useEffect(() => docTaskOptionsStore.setNeedReload(true), []);
  // a message of an earlier visit is not carried into this one
  useEffect(() => useQueryNotice.getState().dismiss(), []);

  if (!docTaskOptionsStore.initiallyLoaded) return <CenteredSpinner />;

  const handleNewQuery = () => {
    useQueryDocumentsStore.getState().setOpUUID("");
    useQueryDocumentsStore.getState().stopPolling();
    useAsked.getState().setPending(null);
    useDocTasksCurrentStore.getState().setNewQuery();
  };

  return (
    <SplitLayout
      listLabel="Query history"
      newLabel="New Query"
      onNew={handleNewQuery}
      list={(afterPick) => <QueriesListBar afterPick={afterPick} />}
    >
      {(headTools) => (
        <div className="scroll-soft h-full overflow-y-auto">
          <div className="mx-auto flex min-h-full w-full flex-col gap-3 px-1 pb-1">
            <PageHead>{headTools}</PageHead>
            <ResponseArea />
            <QueryArea />
          </div>
        </div>
      )}
    </SplitLayout>
  );
}
