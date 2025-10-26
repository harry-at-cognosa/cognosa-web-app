// src/components/SuperuserRoute.tsx
import { Outlet } from "react-router-dom";
import { useLoggedUserStore } from "../stores/useLoggedUserStore";

export default function GroupAdminRoute() {
  const { is_groupadmin } = useLoggedUserStore();

  if (!is_groupadmin) return null;

  // Allow access
  return <Outlet />;
}
