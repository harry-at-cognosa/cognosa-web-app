import { useRef } from "react";
import { useColumnWidths } from "../hooks/useColumnWidths";
import styles from "./HeaderColumnsRow.module.css";

interface Props {
  table: string;
  col: string;
}

// Grip on the right edge of a header cell. Drag to set the column width,
// double-click to go back to the default width.
export default function ColumnResizeHandle({ table, col }: Props) {
  const { setWidth, resetWidth, persist } = useColumnWidths();
  const drag = useRef<{ startX: number; startWidth: number } | null>(null);

  return (
    <span
      className={styles.resizeHandle}
      title="Drag to resize. Double-click to reset."
      onClick={(e) => e.stopPropagation()}
      onDoubleClick={(e) => {
        e.stopPropagation();
        resetWidth(table, col);
      }}
      onPointerDown={(e) => {
        const th = e.currentTarget.closest("th");
        if (!th) return;
        e.preventDefault();
        e.currentTarget.setPointerCapture(e.pointerId);
        drag.current = {
          startX: e.clientX,
          startWidth: th.getBoundingClientRect().width,
        };
        document.body.classList.add(styles.resizing);
      }}
      onPointerMove={(e) => {
        if (!drag.current) return;
        setWidth(
          table,
          col,
          drag.current.startWidth + e.clientX - drag.current.startX
        );
      }}
      onPointerUp={(e) => {
        if (!drag.current) return;
        drag.current = null;
        e.currentTarget.releasePointerCapture(e.pointerId);
        document.body.classList.remove(styles.resizing);
        persist();
      }}
      onPointerCancel={() => {
        drag.current = null;
        document.body.classList.remove(styles.resizing);
      }}
    ></span>
  );
}
