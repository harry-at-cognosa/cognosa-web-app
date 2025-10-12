import { create } from "zustand";

interface NavbarState {
  title: string;
  setTitle: (title: string) => void;
}

export const useNavbarStore = create<NavbarState>((set) => ({
  title: "",
  setTitle: (title) => set({ title }),
}));
