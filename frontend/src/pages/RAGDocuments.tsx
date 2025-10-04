import { Container } from "react-bootstrap";
import QueriesListBar from "./elements/RAGDocuments/QueriesListBar";
import QueryArea from "./elements/RAGDocuments/QueryArea";
import ResponseArea from "./elements/RAGDocuments/ResponseArea";
import { useTopNavBarTitle } from "../hooks/useTopNavBarTitle";

const RAGDocuments = () => {
  useTopNavBarTitle("RAG Documents");

  return (
    <Container fluid style={{ height: "calc(100vh - 60px)" }}>
      <div className="row h-100">
        {/* Sidebar */}
        <div className="col-3 h-100 overflow-auto border-end">
          <QueriesListBar />
        </div>

        {/* Main content */}
        <div className="col-9 d-flex flex-column h-100">
          <div className="">
            <QueryArea />
          </div>
          <div className="">
            <ResponseArea />
          </div>
        </div>
      </div>
    </Container>
  );
};

export default RAGDocuments;
