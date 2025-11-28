import { useEffect } from "react";
import { useWebAppOptionsStore } from "../stores/useWebAppOptionsStore";

export default function ThemeColor() {
  const { color, needReload } = useWebAppOptionsStore();

  useEffect(() => {
    if (needReload) return;
    document.documentElement.style.setProperty("--theme-color-100", color.c100);
    document.documentElement.style.setProperty("--theme-color-200", color.c200);
    document.documentElement.style.setProperty("--theme-color-300", color.c300);
    document.documentElement.style.setProperty("--theme-color-400", color.c400);
    document.documentElement.style.setProperty("--theme-color-500", color.c500);
    document.documentElement.style.setProperty("--theme-color-600", color.c600);
    document.documentElement.style.setProperty("--theme-color-700", color.c700);
    document.documentElement.style.setProperty("--theme-color-800", color.c800);
    document.documentElement.style.setProperty("--theme-color-900", color.c900);
  }, [needReload]);

  return null;
}
