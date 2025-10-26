import { useEffect } from "react";
import { useLoggedUserStore } from "../../stores/useLoggedUserStore";
import { resetAllStores } from "../../api/createResettableStore";

export default function LogoutPage() {
  const { clearLoggedUser } = useLoggedUserStore();

  useEffect(() => {
    clearLoggedUser();
    localStorage.removeItem("token");
    resetAllStores();
    window.location.replace("/login");
  }, []);
  return <div>Logout</div>;
}
