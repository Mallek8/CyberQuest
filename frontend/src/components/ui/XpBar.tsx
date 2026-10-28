export function XpBar({
  xp,
  into,
  total,
}: {
  xp: number;
  into: number;
  total: number;
}) {
  const width = total === 0 ? 0 : Math.min(100, Math.round((into / total) * 100));
  const label =
    into === 0 && xp > 0
      ? "New level reached. Progress toward the next level starts again."
      : `${into} / ${total} XP toward the next level`;
  return (
    <div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10" aria-hidden="true">
        <div
          className="h-2 rounded-full bg-gradient-to-r from-cyan-300 to-mint"
          style={{ width: `${width}%` }}
        />
      </div>
      <p className="mt-2 text-xs text-slate-400">{label}</p>
    </div>
  );
}
