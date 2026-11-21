import { create } from "zustand";

interface UsersMeResponse {
  id: string;
  group_id: number;
  group_name: string;
  email: string;
  user_name: string;
  full_name: string;
  is_groupadmin: boolean;
  is_contentmanager: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  // Chat (conversation mode): on for the user's group?  Port of the chat
  // service when the browser must call it directly ("" = same origin).
  chat_enabled?: boolean;
  chat_service_port?: string;
}

interface LoggedUserState extends UsersMeResponse {
  isLogged: boolean;
  setLoggedUser: (data: UsersMeResponse) => void;
  clearLoggedUser: () => void;
}

const defaultValues = {
  isLogged: false,
  id: "",
  user_id: -1,
  group_id: -1,
  group_name: "",
  email: "",
  user_name: "",
  full_name: "",
  is_groupadmin: false,
  is_contentmanager: false,
  is_verified: false,
  is_superuser: false,
  chat_enabled: false,
  chat_service_port: "",
};

export const useLoggedUserStore = create<LoggedUserState>((set) => ({
  ...defaultValues,
  setLoggedUser: (data) => set({ ...data, isLogged: true }),
  clearLoggedUser: () => set(defaultValues),
}));
