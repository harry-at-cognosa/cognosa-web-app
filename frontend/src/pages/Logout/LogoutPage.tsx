import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useLoggedUserStore } from "../../stores/useLoggedUserStore";
import { resetAllStores } from "../../api/createResettableStore";

export default function LogoutPage() {
  const { clearLoggedUser } = useLoggedUserStore();
  const navigate = useNavigate();

  useEffect(() => {
    resetAllStores();
    clearLoggedUser();
    localStorage.removeItem("token");
    navigate("/login");
  }, []);
  return <div>Logout</div>;
}
