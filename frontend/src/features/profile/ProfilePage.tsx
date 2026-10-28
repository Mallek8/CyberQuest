import { useQuery } from "@tanstack/react-query";

import { Spinner } from "../../components/ui/Spinner";
import { XpBar } from "../../components/ui/XpBar";
import { useAuth } from "../../hooks/useAuth";
import { api } from "../../services/apiClient";
import type { AttemptRecord } from "../../types/api";
import { formatWhen } from "../../utils/format";

export function ProfilePage() {
  const { user } = useAuth();
  const attempts = useQuery({
    queryKey: ["attempts"],
    queryFn: () => api<AttemptRecord[]>("/progress/attempts"),
  });

  if (!user) return null;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold">{user.display_name}</h1>
        <p className="mt-2 text-slate-300">
          @{user.username} / {user.email}
        </p>
      </div>
      <section className="rounded-2xl border border-white/10 bg-panel/80 p-5">
        <p className="text-sm text-slate-400">Level {user.level}</p>
        <p className="mt-1 text-2xl font-semibold">{user.xp} XP</p>
        <div className="mt-4">
          <XpBar xp={user.xp} into={user.xp_into_level} total={user.xp_per_level} />
        </div>
        <p className="mt-4 text-sm text-slate-400">Joined {formatWhen(user.created_at)}</p>
      </section>
      <section>
        <h2 className="text-xl font-semibold">Attempt history</h2>
        {attempts.isLoading ? <div className="mt-4"><Spinner label="Loading history" /></div> : null}
        {attempts.isError ? <p className="mt-4 text-rose-300">History could not be loaded.</p> : null}
        {attempts.data && attempts.data.length === 0 ? (
          <p className="mt-4 text-slate-400">No attempts yet.</p>
        ) : null}
        {attempts.data && attempts.data.length > 0 ? (
          <div className="mt-4 overflow-x-auto rounded-2xl border border-white/10">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-white/5 text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">When</th>
                  <th className="px-4 py-3 font-medium">Mission</th>
                  <th className="px-4 py-3 font-medium">Score</th>
                  <th className="px-4 py-3 font-medium">XP</th>
                </tr>
              </thead>
              <tbody>
                {attempts.data.map((attempt) => (
                  <tr key={attempt.id} className="border-t border-white/10">
                    <td className="px-4 py-3">{formatWhen(attempt.created_at)}</td>
                    <td className="px-4 py-3">{attempt.mission_title}</td>
                    <td className="px-4 py-3">
                      {attempt.score}/{attempt.max_score} {attempt.passed ? "cleared" : "below pass"}
                    </td>
                    <td className="px-4 py-3">{attempt.xp_awarded}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </div>
  );
}
