import { useSyncExternalStore } from "react";

const query = "(max-width: 767px)";
function subscribe(cb: () => void) {
  const m = window.matchMedia(query);
  m.addEventListener("change", cb);
  return () => m.removeEventListener("change", cb);
}

/** True below Tailwind's md breakpoint. Presentation only: no behaviour depends on it. */
export function useIsPhone() {
  return useSyncExternalStore(subscribe, () => window.matchMedia(query).matches);
}
