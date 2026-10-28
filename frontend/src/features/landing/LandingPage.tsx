import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { PublicHeader } from "../../components/layout/PublicHeader";
import { buttonClass } from "../../components/ui/Button";
import { useAuth } from "../../hooks/useAuth";
import { api } from "../../services/apiClient";
import type { MissionSummary } from "../../types/api";
import { categoryLabel, titleCase } from "../../utils/format";

const fallbackMissions = [
  {
    slug: "phishing-investigation",
    title: "Phishing Investigation",
    description: "Review a forwarded email and mark the observations that belong in the incident report.",
    category: "phishing",
    difficulty: "beginner",
    xp_reward: 120,
  },
  {
    slug: "security-log-analysis",
    title: "Security Log Analysis",
    description: "Filter a short identity log and select the rows that belong to one suspicious sequence.",
    category: "logs",
    difficulty: "intermediate",
    xp_reward: 160,
  },
  {
    slug: "anomaly-detection",
    title: "Anomaly Detection",
    description: "Compare network indicators with their baselines and mark the rows the change notes do not explain.",
    category: "anomaly",
    difficulty: "intermediate",
    xp_reward: 200,
  },
];

export function LandingPage() {
  const { user } = useAuth();
  const missions = useQuery({
    queryKey: ["missions", "public"],
    queryFn: () => api<MissionSummary[]>("/missions"),
    retry: false,
  });
  const cards = missions.data ?? fallbackMissions;

  return (
    <div className="min-h-screen">
      <PublicHeader />
      <main>
        <section className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-12 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="rise">
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-cyan-200/80">
              AI-Powered Cybersecurity Challenge Game
            </p>
            <h1 className="mt-4 text-5xl font-semibold tracking-tight sm:text-6xl">CyberQuest</h1>
            <p className="mt-5 max-w-xl text-lg text-slate-300">
              Work fictional incidents as an analyst. Mark the signals, submit your read, and take
              the score from the server. Hints still work when no external model is configured.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to={user ? "/app" : "/register"} className={buttonClass("primary")}>
                Start your mission
              </Link>
              <a href="#missions" className={buttonClass("ghost")}>
                See the cases
              </a>
            </div>
          </div>
          <aside className="rise rounded-3xl border border-cyan-300/20 bg-panel/80 p-5 shadow-glow">
            <p className="font-mono text-xs text-mint">Example session</p>
            <pre className="mt-4 overflow-x-auto font-mono text-sm leading-7 text-slate-200">
              {`> mission phishing-investigation
> signals marked        4
> server score          86
> xp awarded            +103
> badge                 phish hunter`}
            </pre>
            <p className="mt-4 text-xs text-slate-400">
              Illustrative numbers, not a saved run. Links inside missions stay as plain text.
            </p>
          </aside>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-8">
          <h2 className="text-2xl font-semibold">How a case works</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {[
              ["Read the brief", "Each mission is a fixed scenario with the artifact an analyst would open."],
              ["Mark what matters", "The server scores precision and recall, so selecting everything is not a free win."],
              ["Keep the XP", "A passing score updates your level, history, and badges. Replays do not farm points."],
            ].map(([title, text], index) => (
              <article key={title} className="rounded-2xl border border-white/10 bg-panel/80 p-5">
                <p className="font-mono text-xs text-cyan-200">Step {index + 1}</p>
                <h3 className="mt-3 text-lg font-semibold">{title}</h3>
                <p className="mt-2 text-sm text-slate-300">{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="missions" className="mx-auto max-w-6xl px-4 py-8">
          <div className="flex items-end justify-between gap-4">
            <h2 className="text-2xl font-semibold">Three playable missions</h2>
            {missions.isError ? (
              <p className="text-sm text-slate-400">The API is offline, so these cards are the built-in catalog.</p>
            ) : null}
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {cards.map((mission) => (
              <article key={mission.slug} className="rounded-2xl border border-cyan-300/15 bg-panel/80 p-5">
                <p className="text-xs uppercase tracking-wide text-cyan-200/80">
                  {categoryLabel(mission.category)} / {titleCase(mission.difficulty)}
                </p>
                <h3 className="mt-3 text-xl font-semibold">{mission.title}</h3>
                <p className="mt-2 text-sm text-slate-300">{mission.description}</p>
                <p className="mt-4 font-mono text-sm text-mint">{mission.xp_reward} XP</p>
              </article>
            ))}
          </div>
        </section>

        <section className="mx-auto grid max-w-6xl gap-6 px-4 py-10 lg:grid-cols-[0.9fr_1.1fr]">
          <div>
            <h2 className="text-2xl font-semibold">Hint assistant</h2>
            <p className="mt-3 text-slate-300">
              The tutor knows which mission is open and returns the next of three curated hints. It
              does not receive the answer key. If you set an OpenAI-compatible endpoint on the API,
              it can paraphrase those hints. Without a key, the curated text is used as-is. The
              browser never sees the provider key.
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-ink/70 p-5 font-mono text-sm text-slate-300">
            <p className="text-cyan-200">hint 1 of 3</p>
            <p className="mt-3">
              Start with identity. Put the domain in the From address next to the company domain
              from the case brief.
            </p>
          </div>
        </section>
      </main>
      <footer className="mx-auto max-w-6xl px-4 py-10 text-sm text-slate-500">
        Educational fiction. Do not put real secrets into the app.
      </footer>
    </div>
  );
}
