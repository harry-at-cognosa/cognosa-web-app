import { create } from "zustand";

interface LoggedUserState {
  isLogged: boolean;
  id: number;
  groupId: number;
  email: string;
  fullName: string;
  is_superuser: boolean;
  setLoggedUser: (
    id: number,
    groupId: number,
    email: string,
    fullName: string,
    is_superuser: boolean
  ) => void;
  clearLoggedUser: () => void;
}

export const useLoggedUserStore = create<LoggedUserState>((set) => ({
  isLogged: false,
  id: -1,
  groupId: -1,
  email: "",
  fullName: "",
  is_superuser: false,
  setLoggedUser: (id, groupId, email, fullName, is_superuser) =>
    set({ isLogged: true, id, groupId, email, fullName, is_superuser }),
  clearLoggedUser: () =>
    set({
      isLogged: false,
      id: -1,
      groupId: -1,
      email: "",
      fullName: "",
      is_superuser: false,
    }),
}));
