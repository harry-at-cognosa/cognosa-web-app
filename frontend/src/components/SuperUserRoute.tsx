// src/components/SuperuserRoute.tsx
import { Outlet } from "react-router-dom";
import { useLoggedUserStore } from "../stores/useLoggedUserStore";

export default function SuperuserRoute() {
  const { is_superuser } = useLoggedUserStore();

  if (!is_superuser) return null;

  // Allow access
  return <Outlet />;
}
