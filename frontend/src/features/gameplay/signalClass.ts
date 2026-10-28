export function signalClass(active: boolean): string {
  const base = "w-full rounded-xl border px-4 py-3 text-left transition";
  if (active) {
    return `${base} border-cyan-300/70 bg-cyan-300/10 text-cyan-50`;
  }
  return `${base} border-white/10 bg-white/5 text-slate-200 hover:border-cyan-300/40`;
}
