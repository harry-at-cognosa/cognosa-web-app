import { useEffect } from "react";
import { useLoggedUserStore } from "../../stores/useLoggedUserStore";
import { resetAllStores } from "../../api/createResettableStore";

export default function LogoutPage() {
  const { clearLoggedUser } = useLoggedUserStore();

  useEffect(() => {
    clearLoggedUser();
    localStorage.removeItem("token");
    resetAllStores();
    setTimeout(() => window.location.replace("/login"), 100);
  }, []);
  return <div>Logout</div>;
}
