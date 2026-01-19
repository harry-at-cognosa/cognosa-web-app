import QueriesListBar from "./components/QueriesListBar";
import QueryArea from "./components/QueryArea";
import ResponseArea from "./components/ResponseArea";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import styles from "./QueryDocumentsPage.module.css";
import clsx from "clsx";
import { useEffect } from "react";
import { useDocTaskOptionsStore } from "./stores/useDocTaskOptionsStore";
import CenteredSpinner from "../../components/CenteredSpinner";
import { useDefaultGVDBsRetrParamsStore } from "../../components/GVDBsRetrParams/useDefaultGVDBsRetrParamsStore";
import { useDocTasksGVDBsRetrParamsStore } from "../../components/GVDBsRetrParams/useDocTasksGVDBsRetrParamsStore";

export default function QueryDocumentsPage() {
  useTopNavBarTitle("Query Documents");
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const defGVDBsRetrParamsStore = useDefaultGVDBsRetrParamsStore();
  const curGVDBsRetrParamsStore = useDocTasksGVDBsRetrParamsStore();

  useEffect(() => {
    if (!docTaskOptionsStore.needReload) return;
    async function fetchDocTaskOptions() {
      await docTaskOptionsStore.fetchData();
    }
    fetchDocTaskOptions();
  }, [docTaskOptionsStore.needReload]);
  useEffect(() => docTaskOptionsStore.setNeedReload(true), []);

  useEffect(() => {
    if (docTaskOptionsStore.needReload) return;
    const newData = docTaskOptionsStore.data.gvdbs_def_retr_params;
    if (!defGVDBsRetrParamsStore.isLoaded && newData)
      defGVDBsRetrParamsStore.setData(newData);
    else curGVDBsRetrParamsStore.copyFromDefault();
  }, [docTaskOptionsStore.needReload, defGVDBsRetrParamsStore.isLoaded]);

  if (!defGVDBsRetrParamsStore.isLoaded) return <CenteredSpinner />;

  return (
    <div className={styles.wrapper}>
      <div className={styles.splitContainer}>
        <div className={clsx("ps-2", "pe-2", styles.leftPanel)}>
          {/* Sidebar */}
          <QueriesListBar />
        </div>
        <div className={clsx("p-0", styles.rightPanel)}>
          <QueryArea />
          <ResponseArea />
        </div>
      </div>
    </div>
  );
}
