import type { EmailContent, Indicator } from "../../types/api";
import { signalClass } from "./signalClass";

export function PhishingView({
  email,
  indicators,
  selected,
  onToggle,
}: {
  email: EmailContent;
  indicators: Indicator[];
  selected: string[];
  onToggle: (id: string) => void;
}) {
  return (
    <div className="space-y-5">
      <article className="overflow-hidden rounded-2xl border border-cyan-300/20 bg-[#0b1220]">
        <header className="border-b border-white/10 px-5 py-4">
          <p className="font-mono text-xs text-cyan-200/80">Forwarded message</p>
          <h2 className="mt-2 text-xl font-semibold">{email.subject}</h2>
          <dl className="mt-4 space-y-1 text-sm text-slate-300">
            <div>
              <dt className="inline text-slate-500">From: </dt>
              <dd className="inline">
                {email.from_name} &lt;{email.from_address}&gt;
              </dd>
            </div>
            <div>
              <dt className="inline text-slate-500">Reply-To: </dt>
              <dd className="inline">{email.reply_to}</dd>
            </div>
            <div>
              <dt className="inline text-slate-500">Date: </dt>
              <dd className="inline">{email.date}</dd>
            </div>
          </dl>
        </header>
        <pre className="whitespace-pre-wrap px-5 py-4 font-sans text-sm leading-6 text-slate-200">
          {email.body}
        </pre>
        <div className="border-t border-white/10 px-5 py-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Headers</p>
          <ul className="mt-2 space-y-2 font-mono text-xs text-slate-300">
            {email.headers.map((header) => (
              <li key={header.name}>
                <span className="text-cyan-200">{header.name}: </span>
                {header.value}
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-500">Links are shown as text on purpose.</p>
        </div>
      </article>
      <div className="space-y-3">
        {indicators.map((indicator) => {
          const active = selected.includes(indicator.id);
          return (
            <button
              key={indicator.id}
              type="button"
              aria-pressed={active}
              className={signalClass(active)}
              onClick={() => onToggle(indicator.id)}
            >
              <span className="block text-xs uppercase tracking-wide text-slate-400">{indicator.group}</span>
              <span className="mt-1 block font-medium">{indicator.label}</span>
              <span className="mt-1 block text-sm text-slate-300">{indicator.detail}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
