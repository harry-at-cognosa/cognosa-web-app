// src/components/SuperuserRoute.tsx
import { Navigate, Outlet } from "react-router-dom";
import { useLoggedUserStore } from "../stores/useLoggedUserStore";

export default function SuperuserRoute() {
  const { isLogged, is_superuser } = useLoggedUserStore();

  if (!isLogged) {
    return <Navigate to="/login" replace />;
  }

  if (!is_superuser) {
    return <Navigate to="/" replace />;
  }

  // Allow access
  return <Outlet />;
}
