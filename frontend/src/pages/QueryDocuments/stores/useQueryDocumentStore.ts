import { createResettableStore } from "../../../api/createResettableStore";

interface QueryDocumentsState {
  opUUID: string;
  setOpUUID: (opUUID: string) => void;
  isPolling: boolean;
  pollingTimeout: number | null;
  clearTimeout: () => void;
  setPollingTimeout: (
    uuid: string,
    pollingFunction: (uuid: string) => void
  ) => void;
  stopPolling: () => void;
}

export const useQueryDocumentsStore =
  createResettableStore<QueryDocumentsState>((set, get) => ({
    opUUID: "",
    setOpUUID: (opUUID: string) => set({ opUUID }),
    isPolling: false,
    pollingTimeout: null,
    clearTimeout: () => {
      const curTimeout = get().pollingTimeout;
      if (curTimeout) clearTimeout(curTimeout);
      set({ pollingTimeout: null, isPolling: false });
    },
    setPollingTimeout: (
      uuid: string,
      pollingFunction: (uuid: string) => void
    ) => {
      get().clearTimeout();
      const pollingTimeout = setTimeout(() => pollingFunction(uuid), 1000);
      set({ pollingTimeout, isPolling: true });
    },
    stopPolling: () => {
      get().clearTimeout();
    },
  }));
