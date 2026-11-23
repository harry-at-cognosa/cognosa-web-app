import { useEffect } from "react";
import { useLoggedUserStore } from "../../stores/useLoggedUserStore";
import { resetAllStores } from "../../api/createResettableStore";
import { PageHead } from "@/components/Shell";

export default function LogoutPage() {
  const { clearLoggedUser } = useLoggedUserStore();

  useEffect(() => {
    clearLoggedUser();
    localStorage.removeItem("token");
    resetAllStores();
    setTimeout(() => window.location.replace("/login"), 100);
  }, []);
  return (
    <div className="px-5 pt-3">
      <PageHead title="Logout" />
    </div>
  );
}
