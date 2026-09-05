import { useCallback, useState } from "react";

// Feature 198: draggable separator between the queries list (left) and the
// query/response area (right). Width is a percentage of the container,
// clamped to [MIN_PCT, MAX_PCT], persisted per browser in localStorage.
const STORAGE_KEY = "query_page_left_panel_pct";
export const DEFAULT_PCT = 33.333;
const MIN_PCT = 18;
const MAX_PCT = 45;

function clamp(pct: number): number {
  return Math.min(MAX_PCT, Math.max(MIN_PCT, pct));
}

export function useLeftPanelPct(): [number, (pct: number) => void] {
  const [pct, setPctState] = useState<number>(() => {
    try {
      const saved = Number(localStorage.getItem(STORAGE_KEY));
      return saved > 0 ? clamp(saved) : DEFAULT_PCT;
    } catch {
      return DEFAULT_PCT;
    }
  });
  const setPct = useCallback((value: number) => {
    const v = clamp(value);
    setPctState(v);
    try {
      localStorage.setItem(STORAGE_KEY, String(v));
    } catch {
      /* ignore storage errors */
    }
  }, []);
  return [pct, setPct];
}
