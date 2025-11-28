import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import MarkdownRenderer from "../../../components/MarkdownRenderer";
import { useState } from "react";
import { Button } from "react-bootstrap";
import clsx from "clsx";

function ResponseArea() {
  const { question_number, output_text, output_text_2 } =
    useDocTasksCurrentStore();
  const [isHovered1, setIsHovered1] = useState(false);
  const [isHovered2, setIsHovered2] = useState(false);
  const [showFirst, setShowFirst] = useState(false);
  const hasSecond = question_number >= 2;
  const content = hasSecond && !showFirst ? output_text_2 : output_text;
  const bgColor1 = isHovered1 || showFirst ? "bg-tc-300" : "bg-tc-100";
  const bgColor2 = isHovered2 || !showFirst ? "bg-tc-300" : "bg-tc-100";
  return (
    <>
      {hasSecond ? (
        <span>
          <Button
            type="button"
            size="sm"
            className={clsx("mx-1 fw-bold", bgColor1)}
            variant=""
            onMouseEnter={() => setIsHovered1(true)}
            onMouseLeave={() => setIsHovered1(false)}
            onClick={() => setShowFirst(true)}
            style={{ backgroundColor: bgColor1 }}
          >
            Answer 1
          </Button>
          <Button
            type="button"
            size="sm"
            className={clsx("mx-1 fw-bold", bgColor2)}
            variant=""
            onMouseEnter={() => setIsHovered2(true)}
            onMouseLeave={() => setIsHovered2(false)}
            onClick={() => setShowFirst(false)}
          >
            Answer 2
          </Button>
        </span>
      ) : null}
      <div
        className="response-area p-3 overflow-auto bg-white"
        style={{
          wordWrap: "break-word",
          wordBreak: "break-word",
          overflowWrap: "break-word",
        }}
      >
        {content ? (
          <MarkdownRenderer content={content} />
        ) : (
          <p className="text-muted">
            <em>Response will appear here...</em>
          </p>
        )}
      </div>
    </>
  );
}

export default ResponseArea;
