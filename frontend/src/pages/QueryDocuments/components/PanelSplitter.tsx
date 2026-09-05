import { useCallback, useEffect, useRef } from "react";
import styles from "../QueryDocumentsPage.module.css";

import { DEFAULT_PCT } from "../hooks/useLeftPanelPct";

interface Props {
  containerRef: React.RefObject<HTMLDivElement | null>;
  onChange: (pct: number) => void;
}

export default function PanelSplitter({ containerRef, onChange }: Props) {
  const dragging = useRef(false);

  const pctFromEvent = useCallback(
    (clientX: number): number | null => {
      const el = containerRef.current;
      if (!el) return null;
      const rect = el.getBoundingClientRect();
      if (rect.width <= 0) return null;
      return ((clientX - rect.left) / rect.width) * 100;
    },
    [containerRef],
  );

  useEffect(() => {
    const onMove = (e: PointerEvent) => {
      if (!dragging.current) return;
      const pct = pctFromEvent(e.clientX);
      if (pct !== null) onChange(pct);
    };
    const onUp = () => {
      if (!dragging.current) return;
      dragging.current = false;
      document.body.classList.remove(styles.resizing);
    };
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    window.addEventListener("pointercancel", onUp);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      window.removeEventListener("pointercancel", onUp);
    };
  }, [pctFromEvent, onChange]);

  return (
    <div
      className={styles.splitter}
      role="separator"
      aria-orientation="vertical"
      title="Drag to resize. Double-click to reset."
      onPointerDown={(e) => {
        e.preventDefault();
        dragging.current = true;
        document.body.classList.add(styles.resizing);
      }}
      onDoubleClick={() => onChange(DEFAULT_PCT)}
    />
  );
}
