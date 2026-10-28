import { useMemo, useState } from "react";

import type { AnomalyEvent } from "../../types/api";
import { signalClass } from "./signalClass";

const metricLabels: Record<string, string> = {
  outbound_mbps: "Outbound",
  dns_queries: "DNS queries",
  unique_dest_ips: "Unique destinations",
  failed_auth: "Failed sign-ins",
};

export function AnomalyView({
  events,
  selected,
  onToggle,
}: {
  events: AnomalyEvent[];
  selected: string[];
  onToggle: (id: string) => void;
}) {
  const [metric, setMetric] = useState("all");
  const metrics = useMemo(() => Array.from(new Set(events.map((event) => event.metric))), [events]);
  const visible = events.filter((event) => metric === "all" || event.metric === metric);
  const maxByMetric = useMemo(() => {
    const maxes: Record<string, number> = {};
    for (const event of events) {
      const peak = Math.max(event.value, event.baseline, 1);
      maxes[event.metric] = Math.max(maxes[event.metric] ?? 0, peak);
    }
    return maxes;
  }, [events]);

  return (
    <div className="space-y-4">
      <label className="block max-w-xs text-sm">
        <span className="mb-1 block text-slate-400">Metric</span>
        <select
          value={metric}
          onChange={(event) => setMetric(event.target.value)}
          className="w-full rounded-xl border border-white/10 bg-ink px-3 py-2"
        >
          <option value="all">All metrics</option>
          {metrics.map((item) => (
            <option key={item} value={item}>
              {metricLabels[item] ?? item}
            </option>
          ))}
        </select>
      </label>
      <div className="space-y-3">
        {visible.map((event) => {
          const active = selected.includes(event.id);
          const scale = maxByMetric[event.metric] || 1;
          const valueWidth = Math.max(4, Math.round((event.value / scale) * 100));
          const baseWidth = Math.max(2, Math.round((event.baseline / scale) * 100));
          return (
            <button
              key={event.id}
              type="button"
              aria-pressed={active}
              className={signalClass(active)}
              onClick={() => onToggle(event.id)}
            >
              <span className="flex flex-wrap items-baseline justify-between gap-2">
                <span className="font-medium">
                  {metricLabels[event.metric] ?? event.metric} at {event.time}
                </span>
                <span className="font-mono text-sm text-cyan-100">
                  {event.value} {event.unit} / baseline {event.baseline}
                </span>
              </span>
              <span className="mt-3 block">
                <span className="relative block h-2 rounded-full bg-white/10">
                  <span
                    className="absolute inset-y-0 left-0 rounded-full bg-cyan-300"
                    style={{ width: `${valueWidth}%` }}
                  />
                  <span
                    className="absolute inset-y-[-3px] w-0.5 bg-mint"
                    style={{ left: `${baseWidth}%` }}
                  />
                </span>
                <span className="mt-1 block text-xs text-slate-500">Cyan is the value. Green marks the baseline.</span>
              </span>
              <span className="mt-2 block text-sm text-slate-300">{event.context}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
