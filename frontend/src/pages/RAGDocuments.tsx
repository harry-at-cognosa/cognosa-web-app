import QueriesListBar from "./elements/RAGDocuments/QueriesListBar";
import QueryArea from "./elements/RAGDocuments/QueryArea";
import ResponseArea from "./elements/RAGDocuments/ResponseArea";
import { useTopNavBarTitle } from "../hooks/useTopNavBarTitle";
import styles from "./RAGDocuments.module.css";
import clsx from "clsx";

const RAGDocuments = () => {
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
};

export default RAGDocuments;
