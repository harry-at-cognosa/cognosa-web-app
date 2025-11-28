import { Card, Container } from "react-bootstrap";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { BoxArrowRight, Link45deg } from "react-bootstrap-icons";
import ServerStatusAll from "./ServerStatusAll";

export default function IndexPage() {
  const [isHovered1, setIsHovered1] = useState(false);
  const navigate = useNavigate();
  useTopNavBarTitle("");
  return (
    <Container className="mt-5">
      <Card
        className="rounded-3 shadow-sm"
        onMouseEnter={() => setIsHovered1(true)}
        onMouseLeave={() => setIsHovered1(false)}
        onClick={() => navigate("query_documents/queries")}
      >
        <Card.Header
          className="fw-bold"
          style={{
            backgroundColor: isHovered1
              ? "var(--theme-color-400)"
              : "var(--theme-color-300)",
          }}
        >
          <BoxArrowRight className="me-2" />
          Query Documents / Queries
          <Link45deg
            className="ms-2"
            style={{ visibility: isHovered1 ? "visible" : "hidden" }}
          />
        </Card.Header>
        <Card.Body className="bg-tc-100">
          <Card.Title>Ask questions across your knowledge base</Card.Title>
          <Card.Text>
            Query any document collection using natural language.
            <br />
            Select document collection, choose an AI model, and refine results
            with custom instructions.
            <br />
            Get precise answers powered by retrieval-augmented generation.
          </Card.Text>
        </Card.Body>
      </Card>
      <ServerStatusAll />
    </Container>
  );
}
