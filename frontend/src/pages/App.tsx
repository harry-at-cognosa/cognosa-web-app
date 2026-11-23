import { useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { Shell } from "../components/Shell";
import { TooltipProvider } from "../components/ui/tooltip";
import { useLoggedUserStore } from "../stores/useLoggedUserStore";
import NavigationInjector from "../api/NavigationInjector";
import { API_URL } from "../api/apiURL";
import { useWebAppOptionsStore } from "../stores/useWebAppOptionsStore";
import ThemeColor from "../components/ThemeColor";

export default function App() {
  const { setLoggedUser } = useLoggedUserStore();
  const navigate = useNavigate();
  const webappOptionsStore = useWebAppOptionsStore();

  useEffect(() => {
    if (!webappOptionsStore.needReload) return;
    webappOptionsStore.fetchData();
  }, [webappOptionsStore.needReload]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.replace("/");
      return;
    }

    async function fetchUser() {
      const res = await fetch(`${API_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const user = await res.json();
        setLoggedUser(user);
      } else {
        window.location.replace("/");
      }
    }

    fetchUser();
  }, [navigate]);

  return (
    <TooltipProvider delayDuration={250}>
      <NavigationInjector />
      <ThemeColor />
      <Shell>
        <Outlet />
      </Shell>
    </TooltipProvider>
  );
}
