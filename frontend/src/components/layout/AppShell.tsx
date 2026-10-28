import { Link, NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { Logo } from "./Logo";

const links = [
  { to: "/app", label: "Dashboard", end: true },
  { to: "/app/missions", label: "Missions", end: false },
  { to: "/app/achievements", label: "Badges", end: false },
  { to: "/app/profile", label: "Profile", end: false },
];

export function AppShell() {
  const { user, logout } = useAuth();
  return (
    <div className="min-h-screen">
      <header className="border-b border-cyan-300/15 bg-ink/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-4 px-4 py-4">
          <Logo to="/app" />
          <nav className="flex flex-wrap gap-1 text-sm">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-1.5 ${isActive ? "bg-cyan-300/15 text-cyan-100" : "text-slate-300 hover:text-white"}`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3 text-sm">
            {user ? (
              <Link to="/app/profile" className="text-slate-300">
                Level {user.level}, {user.xp} XP
              </Link>
            ) : null}
            <button type="button" onClick={logout} className="text-slate-400 hover:text-white">
              Sign out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
