import { useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import TopNavBar from "../components/TopNavBar/TopNavBar";
import { useLoggedUserStore } from "../stores/useLoggedUserStore";
import NavigationInjector from "../api/NavigationInjector";
import { API_URL } from "../api/apiURL";
import { useWebAppOptionsStore } from "../stores/useWebAppOptionsStore";

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
      navigate("/logout");
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
        navigate("/logout");
      }
    }

    fetchUser();
  }, [navigate]);

  return (
    <div className="min-vh-100">
      <NavigationInjector />
      <TopNavBar />
      <main>
        <Outlet />
      </main>
    </div>
  );
}
