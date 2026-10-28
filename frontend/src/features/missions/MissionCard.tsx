import { Link } from "react-router-dom";

import type { MissionSummary } from "../../types/api";
import { categoryLabel, statusLabel, titleCase } from "../../utils/format";

export function MissionCard({ mission }: { mission: MissionSummary }) {
  const locked = mission.status === "locked";
  const body = (
    <article className="h-full rounded-2xl border border-cyan-300/15 bg-panel/80 p-5 transition hover:border-cyan-300/40">
      <div className="flex items-center justify-between gap-3 text-xs uppercase tracking-wide">
        <span className="text-cyan-200">{categoryLabel(mission.category)}</span>
        <span className={mission.status === "completed" ? "text-mint" : "text-slate-400"}>
          {statusLabel(mission.status)}
        </span>
      </div>
      <h3 className="mt-3 text-xl font-semibold">{mission.title}</h3>
      <p className="mt-2 text-sm text-slate-300">{mission.description}</p>
      <dl className="mt-4 grid grid-cols-3 gap-2 text-sm">
        <div>
          <dt className="text-slate-500">Difficulty</dt>
          <dd>{titleCase(mission.difficulty)}</dd>
        </div>
        <div>
          <dt className="text-slate-500">XP</dt>
          <dd className="text-mint">{mission.xp_reward}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Best</dt>
          <dd>{mission.best_score ?? "None"}</dd>
        </div>
      </dl>
    </article>
  );

  if (locked) {
    return <div className="opacity-70">{body}</div>;
  }
  return (
    <Link to={`/app/missions/${mission.slug}`} className="block h-full">
      {body}
    </Link>
  );
}
