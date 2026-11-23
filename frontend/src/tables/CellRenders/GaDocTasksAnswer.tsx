import type { TableRow } from "../TableStoreFactory";
import TextCell from "./TextCell";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface Props {
  row: TableRow;
}

const segBtn =
  "h-6 rounded-full px-2.5 text-[12.5px] font-semibold whitespace-nowrap text-ink-2 hover:bg-tint hover:text-tint-fg";
const segOn = "bg-tint text-tint-fg";

export default function GaDocTasksAnswer({ row }: Props) {
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

  return (
    <div className="flex h-full w-full flex-col gap-1">
      <div
        className="inline-flex flex-none gap-0.5 self-start rounded-full bg-sunk p-[3px]"
        role="group"
        aria-label="Answer shown"
      >
        <button
          type="button"
          className={cn(segBtn, !showLast && segOn)}
          aria-pressed={!showLast}
          onClick={onButtonAnswer1}
        >
          Answer 1
        </button>
        <button
          type="button"
          className={cn(segBtn, showLast && segOn)}
          aria-pressed={showLast}
          onClick={onButtonAnswer2}
        >
          Answer 2
        </button>
      </div>

      <TextCell value={content} rows={6}></TextCell>
    </div>
  );
}
