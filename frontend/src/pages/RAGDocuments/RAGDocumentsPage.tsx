import QueriesListBar from "./components/QueriesListBar";
import QueryArea from "./components/QueryArea";
import ResponseArea from "./components/ResponseArea";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import styles from "./RAGDocumentsPage.module.css";
import clsx from "clsx";

export default function RAGDocumentsPage() {
  useTopNavBarTitle("RAG Documents");

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
