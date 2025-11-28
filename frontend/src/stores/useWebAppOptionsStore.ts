import axiosClient from "../api/axiosClient";
import { createResettableStore } from "../api/createResettableStore";
import getColor from "../api/getColor";

interface WebAppOptionsApiSettings {
  webapp_main_color: string;
}

interface WebAppOptionsColorsState {
  c100: string;
  c200: string;
  c300: string;
  c400: string;
  c500: string;
  c600: string;
  c700: string;
  c800: string;
  c900: string;
}

interface WebAppOptionsState {
  api_settings: WebAppOptionsApiSettings | null;
  color: WebAppOptionsColorsState;
  needReload: boolean;
  setNeedReload: (needReload: boolean) => void;
  fetchData: () => Promise<void>;
}

export const useWebAppOptionsStore = createResettableStore<WebAppOptionsState>(
  (set) => ({
    api_settings: null,
    color: {
      c100: getColor("gray", 100),
      c200: getColor("gray", 200),
      c300: getColor("gray", 300),
      c400: getColor("gray", 400),
      c500: getColor("gray", 500),
      c600: getColor("gray", 600),
      c700: getColor("gray", 700),
      c800: getColor("gray", 800),
      c900: getColor("gray", 900),
    },
    needReload: true,
    setNeedReload: (needReload: boolean) => set({ needReload }),
    fetchData: async () => {
      if (!localStorage.getItem("token")) return;
      try {
        const res = await axiosClient.get<WebAppOptionsState>(
          "/webapp_options"
        );
        const main_color = res.data.api_settings?.webapp_main_color || "gray";
        set({
          api_settings: res.data.api_settings,
          color: {
            c100: getColor(main_color, 100),
            c200: getColor(main_color, 200),
            c300: getColor(main_color, 300),
            c400: getColor(main_color, 400),
            c500: getColor(main_color, 500),
            c600: getColor(main_color, 600),
            c700: getColor(main_color, 700),
            c800: getColor(main_color, 800),
            c900: getColor(main_color, 900),
          },
        });
      } catch (err: any) {
        console.log(
          "webapp_options error: " +
            (err.response?.data?.message || err.message)
        );
      } finally {
        set({ needReload: false });
      }
    },
  })
);
