import { Navigate, Outlet } from "react-router-dom";

import { FullPageSpinner } from "../ui/Spinner";
import { useAuth } from "../../hooks/useAuth";

export function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) {
    return <FullPageSpinner />;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

export function GuestRoute() {
  const { user, loading } = useAuth();
  if (loading) {
    return <FullPageSpinner />;
  }
  if (user) {
    return <Navigate to="/app" replace />;
  }
  return <Outlet />;
}
