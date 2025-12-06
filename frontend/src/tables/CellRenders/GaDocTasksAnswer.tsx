import { Button, ButtonGroup } from "react-bootstrap";
import type { TableRow } from "../TableStoreFactory";
import TextCell from "./TextCell";
import { useState } from "react";
import clsx from "clsx";

interface Props {
  row: TableRow;
}

export default function GaDocTasksAnswer({ row }: Props) {
  const [isHovered1, setIsHovered1] = useState(false);
  const [isHovered2, setIsHovered2] = useState(false);
  const [showLast, setShowLast] = useState(true);
  const text1 = row["output_text"];
  const text2 = row["output_text_2"];
  if (!(text1 || text2)) return null;
  if (!text2) return <TextCell value={text1} rows={7}></TextCell>;
  function onButtonAnswer1() {
    if (showLast) setShowLast(false);
  }
  function onButtonAnswer2() {
    if (!showLast) setShowLast(true);
  }
  const content = showLast ? text2 : text1;
  const bgColor1 = isHovered1 || !showLast ? "bg-tc-300" : "bg-tc-100";
  const bgColor2 = isHovered2 || showLast ? "bg-tc-300" : "bg-tc-100";

  return (
    <div className="d-flex flex-column h-100 w-100">
      {/* Button group with no margins/paddings */}
      <ButtonGroup
        className="flex-shrink-0"
        style={{
          margin: 0,
          padding: 0,
          width: "100%",
          borderTopLeftRadius: 0,
          borderTopRightRadius: 0,
        }}
      >
        <Button
          variant=""
          size="sm"
          className={clsx("mx-0 fw-bold", bgColor1)}
          onClick={onButtonAnswer1}
          onMouseEnter={() => setIsHovered1(true)}
          onMouseLeave={() => setIsHovered1(false)}
          style={{ borderRadius: 0 }}
        >
          Answer 1
        </Button>
        <Button
          variant=""
          size="sm"
          className={clsx("mx-0 fw-bold", bgColor2)}
          onClick={onButtonAnswer2}
          onMouseEnter={() => setIsHovered2(true)}
          onMouseLeave={() => setIsHovered2(false)}
          style={{
            borderRadius: 0,
            backgroundColor: bgColor2,
          }}
        >
          Answer 2
        </Button>
      </ButtonGroup>

      {/* Textarea with no padding/margins */}
      <TextCell value={content} rows={6}></TextCell>
    </div>
  );
}
