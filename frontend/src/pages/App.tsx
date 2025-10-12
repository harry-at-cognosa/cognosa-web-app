import { useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import TopNavBar from "../components/TopNavBar/TopNavBar";
import { useLoggedUserStore } from "../stores/useLoggedUserStore";
import NavigationInjector from "../api/NavigationInjector";
import { API_URL } from "../api/apiURL";

export default function App() {
  const { setLoggedUser } = useLoggedUserStore();
  const navigate = useNavigate();

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
        setLoggedUser(
          Number(user["id"]),
          Number(user["group_id"]),
          user["email"].toString(),
          user["user_name"].toString(),
          user["full_name"].toString(),
          user["is_superuser"]
        );
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
