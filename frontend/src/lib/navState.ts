// View-level state of the navigation sidebar: expanded or icon strip, and which
// menu groups are folded. Remembered per browser; not behaviour of the product,
// so it does not belong in src/stores.
import { create } from "zustand";

const KEY_OPEN = "nav_sidebar_open";
const KEY_FOLDED = "nav_sidebar_folded";

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}
function write(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* not essential */
  }
}

interface NavState {
  open: boolean; // true = expanded, false = icon strip
  folded: string[]; // ids of folded menu groups
  setOpen: (open: boolean) => void;
  setFolded: (id: string, folded: boolean) => void;
}

export const useNav = create<NavState>((set, get) => ({
  open: read(KEY_OPEN) !== "0",
  folded: (read(KEY_FOLDED) || "").split(",").filter(Boolean),
  setOpen: (open) => {
    write(KEY_OPEN, open ? "1" : "0");
    set({ open });
  },
  setFolded: (id, folded) => {
    const next = get().folded.filter((x) => x !== id);
    if (folded) next.push(id);
    write(KEY_FOLDED, next.join(","));
    set({ folded: next });
  },
}));
