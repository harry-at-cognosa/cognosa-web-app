import { create } from "zustand";

// View level only: v1.0.1 reported validation and request errors of the
// Queries page with window.alert(). The same texts are now shown in a
// dismissible Notice above the query form; this holds the text on show.
interface QueryNoticeState {
  text: string | null;
  show: (text: string) => void;
  dismiss: () => void;
}

export const useQueryNotice = create<QueryNoticeState>((set) => ({
  text: null,
  show: (text: string) => set({ text }),
  dismiss: () => set({ text: null }),
}));
