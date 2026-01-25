import axiosClient from "../../api/axiosClient";
import { createResettableStore } from "../../api/createResettableStore";

export type SuChangeOneselfGroup = {
  group_id: number;
  group_name: string;
};

export type SuChangeOneselfGetResult = {
  group_id: number;
  group_list: SuChangeOneselfGroup[];
  is_groupadmin: boolean;
  is_contentmanager: boolean;
};

export type SuChangeOneselfUpdate = {
  group_id: number;
  is_groupadmin: boolean;
  is_contentmanager: boolean;
};

export type SuChangeOneselfUpdateResult = {
  is_success: boolean;
  error_msg: string | null;
  group_id: number;
  is_groupadmin: boolean;
  is_contentmanager: boolean;
};

interface SuChangeOneselfState {
  firstLoad: boolean;
  group_id: number;
  setGroupId: (group_id: number) => void;
  group_list: SuChangeOneselfGroup[];
  is_groupadmin: boolean;
  setIsGroupAdmin: (is_groupadmin: boolean) => void;
  is_contentmanager: boolean;
  setIsContentManager: (is_contentmanager: boolean) => void;
  error_msg: string | null;
  fetchData: () => Promise<void>;
  applyData: () => Promise<SuChangeOneselfUpdateResult | null>;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
}

const endpoint: string = "/su/change_oneself";

export const useSuChangeOneselfStore =
  createResettableStore<SuChangeOneselfState>((set, get) => ({
    firstLoad: true,
    group_id: 0,
    setGroupId: (group_id: number) => set({ group_id }),
    group_list: [],
    is_groupadmin: false,
    setIsGroupAdmin: (is_groupadmin: boolean) => set({ is_groupadmin }),
    is_contentmanager: false,
    setIsContentManager: (is_contentmanager: boolean) =>
      set({ is_contentmanager }),
    error_msg: null,
    fetchData: async () => {
      try {
        const response =
          await axiosClient.get<SuChangeOneselfGetResult>(endpoint);
        const data = response.data;
        set({ ...data, needReload: false, firstLoad: false });
      } catch {
        set({
          needReload: false,
          firstLoad: false,
          error_msg: "Error during GET " + endpoint,
        });
      }
    },
    applyData: async () => {
      const { group_id, is_groupadmin, is_contentmanager } = get();
      const params: SuChangeOneselfUpdate = {
        group_id,
        is_groupadmin,
        is_contentmanager,
      };
      try {
        const response = await axiosClient.put<SuChangeOneselfUpdateResult>(
          endpoint,
          params,
        );
        const data = response.data;
        set({ ...data, needReload: false, firstLoad: false });
        return data;
      } catch {
        set({
          needReload: false,
          firstLoad: false,
          error_msg: "Error during PUT " + endpoint,
        });
        return null;
      }
    },
    needReload: true,
    setNeedReload: (needReload: boolean) => set({ needReload }),
  }));
