import { useEffect } from "react";
import { useWebAppOptionsStore } from "../stores/useWebAppOptionsStore";
import getColor from "../api/getColor";

const TC_SHADES = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900];
const DEFAULT_COLOR = "gray"; // the store's default
const LAST_COLOR_KEY = "webapp_main_color_last";

/** Writes --tc-50 … --tc-900 (the 9b tokens in index.css) on <html>. */
function applyRamp(name: string): boolean {
  if (!getColor(name, 500)) return false;
  for (const shade of TC_SHADES) {
    document.documentElement.style.setProperty(
      `--tc-${shade}`,
      getColor(name, shade)
    );
  }
  return true;
}

// View only: start from the ramp this browser last received, so a reload does
// not flash the default grey before /webapp_options answers. The setting itself
// (webapp_main_color) stays the only source; this is overwritten on every load.
try {
  const last = localStorage.getItem(LAST_COLOR_KEY);
  if (last) applyRamp(last);
} catch {
  /* not essential */
}

export default function ThemeColor() {
  const { needReload, api_settings } = useWebAppOptionsStore();

  useEffect(() => {
    if (needReload) return;
    // 9b tokens; same rule as the store: webapp_main_color, else "gray"
    const name = api_settings?.webapp_main_color || DEFAULT_COLOR;
    const applied = applyRamp(name) ? name : DEFAULT_COLOR;
    if (applied !== name) applyRamp(DEFAULT_COLOR);
    try {
      localStorage.setItem(LAST_COLOR_KEY, applied);
    } catch {
      /* not essential */
    }
  }, [needReload]);

  return null;
}
