import { useRef, type ReactNode } from "react";
import clsx from "clsx";
import { useColumnWidths } from "../hooks/useColumnWidths";
import styles from "./ResizableTableWidth.module.css";

interface Props {
  // table name the width is stored under (same key as its column widths)
  table: string;
  children: ReactNode;
}

const WIDTH_KEY = "__table";
const MIN_TABLE_WIDTH = 480;

// Page wrapper for a table. Until the user drags the grip on its right edge it
// is a normal Bootstrap container; after that it has the dragged width (never
// wider than the window). Double-click the grip to go back to the default.
export default function ResizableTableWidth({ table, children }: Props) {
  const width = useColumnWidths((state) => state.widths[table]?.[WIDTH_KEY]);
  const { setWidth, resetWidth, persist } = useColumnWidths();
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const drag = useRef<{ startX: number; startWidth: number } | null>(null);

  function endDrag() {
    drag.current = null;
    document.body.classList.remove(styles.resizing);
  }

  return (
    <div
      ref={wrapperRef}
      className={clsx(
        styles.wrapper,
        "my-4",
        width ? "mx-auto px-3" : "container"
      )}
      style={width ? { width: width + "px", maxWidth: "100%" } : undefined}
    >
      {children}
      <span
        className={styles.grip}
        title="Drag to make the table wider or narrower. Double-click to reset."
        onDoubleClick={() => resetWidth(table, WIDTH_KEY)}
        onPointerDown={(e) => {
          if (!wrapperRef.current) return;
          e.preventDefault();
          e.currentTarget.setPointerCapture(e.pointerId);
          drag.current = {
            startX: e.clientX,
            startWidth: wrapperRef.current.getBoundingClientRect().width,
          };
          document.body.classList.add(styles.resizing);
        }}
        onPointerMove={(e) => {
          if (!drag.current) return;
          // the wrapper is centred, so the edge moves half as far as the width grows
          const next =
            drag.current.startWidth + 2 * (e.clientX - drag.current.startX);
          setWidth(
            table,
            WIDTH_KEY,
            Math.min(
              Math.max(next, MIN_TABLE_WIDTH),
              document.documentElement.clientWidth
            )
          );
        }}
        onPointerUp={(e) => {
          if (!drag.current) return;
          e.currentTarget.releasePointerCapture(e.pointerId);
          endDrag();
          persist();
        }}
        onPointerCancel={endDrag}
      ></span>
    </div>
  );
}
