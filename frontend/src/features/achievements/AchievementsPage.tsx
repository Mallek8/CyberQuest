import { useQuery } from "@tanstack/react-query";

import { Spinner } from "../../components/ui/Spinner";
import { api } from "../../services/apiClient";
import type { Achievement } from "../../types/api";
import { formatWhen } from "../../utils/format";
import { AchievementIcon } from "./AchievementIcon";

export function AchievementsPage() {
  const achievements = useQuery({
    queryKey: ["achievements"],
    queryFn: () => api<Achievement[]>("/achievements"),
  });

  if (achievements.isLoading) return <Spinner label="Loading badges" />;
  if (achievements.isError || !achievements.data) {
    return <p className="text-rose-300">Badges could not be loaded.</p>;
  }

  return (
    <div>
      <h1 className="text-3xl font-semibold">Badges</h1>
      <p className="mt-2 max-w-2xl text-slate-300">
        Badges are granted by the server when the matching rule is true. Locked cards stay visible
        so the goals are clear.
      </p>
      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {achievements.data.map((badge) => (
          <article
            key={badge.slug}
            className={`rounded-2xl border p-5 ${
              badge.unlocked ? "border-mint/30 bg-panel/90" : "border-white/10 bg-panel/50 text-slate-400"
            }`}
          >
            <div className="flex items-center gap-3">
              <span className={`rounded-lg p-2 ${badge.unlocked ? "bg-mint/10 text-mint" : "bg-white/5"}`}>
                <AchievementIcon name={badge.icon} />
              </span>
              <div>
                <h2 className="font-semibold text-slate-100">{badge.name}</h2>
                <p className="text-xs uppercase tracking-wide">
                  {badge.unlocked ? "Unlocked" : "Locked"}
                </p>
              </div>
            </div>
            <p className="mt-4 text-sm">{badge.description}</p>
            {badge.unlocked_at ? (
              <p className="mt-3 text-xs text-slate-500">{formatWhen(badge.unlocked_at)}</p>
            ) : null}
          </article>
        ))}
      </div>
    </div>
  );
}
