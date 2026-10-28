import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { buttonClass } from "../../components/ui/Button";
import { Spinner } from "../../components/ui/Spinner";
import { XpBar } from "../../components/ui/XpBar";
import { api } from "../../services/apiClient";
import type { DashboardData } from "../../types/api";
import { AchievementIcon } from "../achievements/AchievementIcon";
import { categoryLabel, statusLabel } from "../../utils/format";

export function DashboardPage() {
  const dashboard = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api<DashboardData>("/progress/dashboard"),
  });

  if (dashboard.isLoading) return <Spinner label="Loading dashboard" />;
  if (dashboard.isError || !dashboard.data) {
    return <p className="text-rose-300">The dashboard could not be loaded.</p>;
  }

  const data = dashboard.data;
  const stats = [
    ["Level", String(data.user.level)],
    ["XP", String(data.user.xp)],
    ["Missions cleared", `${data.completed_missions} / ${data.total_missions}`],
    ["Badges", `${data.badges_earned} / ${data.total_badges}`],
  ];

  return (
    <div className="space-y-8">
      <div>
        <p className="text-sm text-cyan-200">Welcome back, {data.user.display_name}</p>
        <h1 className="mt-1 text-3xl font-semibold">Dashboard</h1>
      </div>
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(([label, value]) => (
          <article key={label} className="rounded-2xl border border-white/10 bg-panel/80 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
            <p className="mt-2 text-2xl font-semibold">{value}</p>
          </article>
        ))}
      </section>
      <section className="rounded-2xl border border-cyan-300/15 bg-panel/80 p-5">
        <h2 className="text-lg font-semibold">Level progress</h2>
        <div className="mt-4">
          <XpBar xp={data.user.xp} into={data.user.xp_into_level} total={data.user.xp_per_level} />
        </div>
      </section>
      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-2xl border border-white/10 bg-panel/80 p-5">
          <h2 className="text-lg font-semibold">Next mission</h2>
          {data.next_mission ? (
            <div className="mt-4">
              <p className="text-xs uppercase tracking-wide text-cyan-200">
                {categoryLabel(data.next_mission.category)} / {statusLabel(data.next_mission.status)}
              </p>
              <h3 className="mt-2 text-2xl font-semibold">{data.next_mission.title}</h3>
              <p className="mt-2 text-slate-300">{data.next_mission.description}</p>
              <Link to={`/app/missions/${data.next_mission.slug}`} className={`${buttonClass()} mt-5`}>
                Open mission
              </Link>
            </div>
          ) : (
            <p className="mt-4 text-slate-300">All three missions are cleared.</p>
          )}
        </article>
        <article className="rounded-2xl border border-white/10 bg-panel/80 p-5">
          <h2 className="text-lg font-semibold">Recent badges</h2>
          {data.recent_achievements.length === 0 ? (
            <p className="mt-4 text-sm text-slate-400">Clear a mission or ask for a hint to earn the first one.</p>
          ) : (
            <ul className="mt-4 space-y-3">
              {data.recent_achievements.map((badge) => (
                <li key={badge.slug} className="flex items-center gap-3">
                  <span className="rounded-lg bg-cyan-300/10 p-2 text-cyan-200">
                    <AchievementIcon name={badge.icon} />
                  </span>
                  <span>
                    <span className="block font-medium">{badge.name}</span>
                    <span className="block text-sm text-slate-400">{badge.description}</span>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </article>
      </section>
    </div>
  );
}
