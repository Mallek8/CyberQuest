import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppShell } from "../components/layout/AppShell";
import { GuestRoute, ProtectedRoute } from "../components/layout/ProtectedRoute";
import { LoginPage, RegisterPage } from "../features/auth/AuthPages";
import { AchievementsPage } from "../features/achievements/AchievementsPage";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import { GameplayPage } from "../features/gameplay/GameplayPage";
import { LandingPage } from "../features/landing/LandingPage";
import { MissionListPage } from "../features/missions/MissionListPage";
import { ProfilePage } from "../features/profile/ProfilePage";

function NotFoundPage() {
  return (
    <div className="mx-auto max-w-lg px-4 py-24 text-center">
      <h1 className="text-3xl font-semibold">Page not found</h1>
      <p className="mt-3 text-slate-300">That route is not part of CyberQuest.</p>
      <a href="/" className="mt-6 inline-block text-cyan-200">
        Back to the start
      </a>
    </div>
  );
}

export const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  {
    element: <GuestRoute />,
    children: [
      { path: "/login", element: <LoginPage /> },
      { path: "/register", element: <RegisterPage /> },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: "/app", element: <DashboardPage /> },
          { path: "/app/missions", element: <MissionListPage /> },
          { path: "/app/missions/:slug", element: <GameplayPage /> },
          { path: "/app/achievements", element: <AchievementsPage /> },
          { path: "/app/profile", element: <ProfilePage /> },
        ],
      },
    ],
  },
  { path: "/home", element: <Navigate to="/" replace /> },
  { path: "*", element: <NotFoundPage /> },
]);
