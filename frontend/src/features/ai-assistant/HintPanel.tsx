import type { Achievement, HintHistory } from "../../types/api";

export function HintPanel({
  history,
  pending,
  onRequest,
}: {
  history?: HintHistory;
  pending: boolean;
  onRequest: () => void;
}) {
  const remaining = history?.hints_remaining;
  return (
    <aside className="rounded-2xl border border-white/10 bg-panel/80 p-5">
      <h2 className="text-lg font-semibold">Hint assistant</h2>
      <p className="mt-2 text-sm text-slate-400">
        Hints stay short on purpose. They do not include the answer key.{" "}
        {remaining === undefined ? "Loading hint count." : `${remaining} left on this mission.`}
      </p>
      <button
        type="button"
        onClick={onRequest}
        disabled={pending || remaining === undefined || remaining === 0}
        className="mt-4 w-full rounded-xl border border-cyan-300/30 px-4 py-2 text-sm font-semibold text-cyan-100 disabled:opacity-50"
      >
        {pending ? "Asking" : "Ask for a hint"}
      </button>
      <ol className="mt-5 space-y-3">
        {history?.hints.map((hint) => (
          <li key={hint.hint_level} className="rounded-xl bg-ink/70 p-3 text-sm">
            <p className="font-mono text-xs text-cyan-200">
              Hint {hint.hint_level} / {hint.provider === "llm" ? "language model" : "curated"}
            </p>
            <p className="mt-2 text-slate-200">{hint.content}</p>
          </li>
        ))}
      </ol>
    </aside>
  );
}

export function BadgeNotice({ badges }: { badges: Achievement[] }) {
  if (badges.length === 0) return null;
  return (
    <p className="rounded-xl border border-mint/30 bg-mint/10 px-4 py-3 text-sm text-mint">
      New badge: {badges.map((badge) => badge.name).join(", ")}
    </p>
  );
}
