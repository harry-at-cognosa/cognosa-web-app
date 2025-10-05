import { useEffect } from "react";
import { useNavbarStore } from "../stores/useTopNavBarStore";

const DEFAULT_TITLE = "Cognosa WebApp";

export const useTopNavBarTitle = (title: string) => {
  const setTitle = useNavbarStore((state) => state.setTitle);
  const full_title = DEFAULT_TITLE + (title ? " / " + title : "");

  useEffect(() => {
    setTitle(full_title); // Sync navbar title

    return () => {
      setTitle(DEFAULT_TITLE);
      document.title = DEFAULT_TITLE; // Reset on unmount
    };
  }, [setTitle, title]);
};
