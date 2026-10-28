import type { FeedbackItem } from "../../types/api";

const outcomeLabel: Record<FeedbackItem["outcome"], string> = {
  hit: "Confirmed signal",
  false_alarm: "Benign item",
  missed: "Missed signal",
};

const outcomeClass: Record<FeedbackItem["outcome"], string> = {
  hit: "text-mint",
  false_alarm: "text-amber-300",
  missed: "text-rose-300",
};

export function ResultPanel({
  score,
  maxScore,
  passed,
  xpAwarded,
  summary,
  feedback,
}: {
  score: number;
  maxScore: number;
  passed: boolean;
  xpAwarded: number;
  summary: string;
  feedback: FeedbackItem[];
}) {
  return (
    <section className="rounded-2xl border border-cyan-300/20 bg-panel/90 p-5">
      <p className="text-xs uppercase tracking-wide text-slate-400">Scored on the server</p>
      <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
        <h2 className="text-3xl font-semibold">
          {score}
          <span className="text-lg text-slate-400"> / {maxScore}</span>
        </h2>
        <p className={passed ? "text-mint" : "text-amber-300"}>
          {passed ? `Cleared, +${xpAwarded} XP` : "Below the pass mark"}
        </p>
      </div>
      <p className="mt-3 text-slate-300">{summary}</p>
      <ul className="mt-5 space-y-3">
        {feedback.map((item) => (
          <li key={`${item.outcome}-${item.id}`} className="rounded-xl border border-white/10 px-4 py-3">
            <p className={`text-xs uppercase tracking-wide ${outcomeClass[item.outcome]}`}>
              {outcomeLabel[item.outcome]}
            </p>
            <p className="mt-1 font-medium">{item.label}</p>
            <p className="mt-1 text-sm text-slate-300">{item.explanation}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
