import QueriesListBar from "./components/QueriesListBar";
import QueryArea from "./components/QueryArea";
import ResponseArea from "./components/ResponseArea";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import styles from "./QueryDocumentsPage.module.css";
import clsx from "clsx";
import { useEffect, useRef } from "react";
import { useDocTaskOptionsStore } from "./stores/useDocTaskOptionsStore";
import CenteredSpinner from "../../components/CenteredSpinner";
import PanelSplitter from "./components/PanelSplitter";
import { useLeftPanelPct } from "./hooks/useLeftPanelPct";

export default function QueryDocumentsPage() {
  useTopNavBarTitle("Query Documents");
  const docTaskOptionsStore = useDocTaskOptionsStore();
  const splitRef = useRef<HTMLDivElement | null>(null);
  const [leftPct, setLeftPct] = useLeftPanelPct();

  useEffect(() => {
    if (!docTaskOptionsStore.needReload) return;
    async function fetchDocTaskOptions() {
      await docTaskOptionsStore.fetchData();
    }
    fetchDocTaskOptions();
  }, [docTaskOptionsStore.needReload]);
  useEffect(() => docTaskOptionsStore.setNeedReload(true), []);

  if (!docTaskOptionsStore.initiallyLoaded) return <CenteredSpinner />;

  return (
    <div className={styles.wrapper}>
      <div
        className={styles.splitContainer}
        ref={splitRef}
        style={{ "--left-pct": `${leftPct}%` } as React.CSSProperties}
      >
        <div className={clsx("ps-2", "pe-2", styles.leftPanel)}>
          {/* Sidebar */}
          <QueriesListBar />
        </div>
        <PanelSplitter containerRef={splitRef} onChange={setLeftPct} />
        <div className={clsx("p-0", styles.rightPanel)}>
          <QueryArea />
          <ResponseArea />
        </div>
      </div>
    </div>
  );
}
