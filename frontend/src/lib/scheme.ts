// View-level state: the colour scheme (light, dark, or follow the system).
// Light is the default; the choice is remembered per browser. It sets
// <html data-scheme="light|dark">, which index.css keys its dark tokens on.
// (index.html applies the remembered scheme before first paint as well.)
import { create } from "zustand";

export type Scheme = "light" | "dark" | "system";

export const SCHEME_KEY = "webapp_color_scheme";

function read(): Scheme {
  try {
    const s = localStorage.getItem(SCHEME_KEY);
    return s === "dark" || s === "system" ? s : "light";
  } catch {
    return "light";
  }
}

function resolveDark(scheme: Scheme) {
  return (
    scheme === "dark" ||
    (scheme === "system" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches)
  );
}

function applyScheme(scheme: Scheme) {
  document.documentElement.dataset.scheme = resolveDark(scheme)
    ? "dark"
    : "light";
}

interface SchemeState {
  scheme: Scheme;
  /** resolved scheme, for code that needs a value rather than CSS */
  isDark: boolean;
  setScheme: (scheme: Scheme) => void;
}

const initial = read();

export const useScheme = create<SchemeState>((set) => ({
  scheme: initial,
  isDark: resolveDark(initial),
  setScheme: (scheme) => {
    try {
      localStorage.setItem(SCHEME_KEY, scheme);
    } catch {
      /* not essential */
    }
    applyScheme(scheme);
    set({ scheme, isDark: resolveDark(scheme) });
  },
}));

applyScheme(initial);
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", () => {
    const cur = useScheme.getState();
    if (cur.scheme === "system") cur.setScheme("system");
  });
