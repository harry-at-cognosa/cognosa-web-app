import { useEffect } from "react";
import { useTitle } from "react-use";
import { useNavbarStore } from "../stores/useTopNavBarStore";

const DEFAULT_TITLE = "Cognosa WebApp";

export const useTopNavBarTitle = (title: string) => {
  const setTitle = useNavbarStore((state) => state.setTitle);
  const full_title = DEFAULT_TITLE + (title ? " / " + title : "");
  useTitle(full_title); // Sync browser title

  useEffect(() => {
    setTitle(full_title); // Sync navbar title

    return () => {
      setTitle(DEFAULT_TITLE);
      document.title = DEFAULT_TITLE; // Reset on unmount
    };
  }, [setTitle, title]);
};
