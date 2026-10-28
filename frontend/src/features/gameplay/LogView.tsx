import { useMemo, useState } from "react";

import type { LogEvent } from "../../types/api";
import { signalClass } from "./signalClass";

export function LogView({
  logs,
  selected,
  onToggle,
}: {
  logs: LogEvent[];
  selected: string[];
  onToggle: (id: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState("all");
  const [eventType, setEventType] = useState("all");
  const types = useMemo(() => Array.from(new Set(logs.map((log) => log.event_type))), [logs]);
  const visible = logs.filter((log) => {
    const haystack = `${log.message} ${log.actor} ${log.ip} ${log.location}`.toLowerCase();
    const matchesQuery = haystack.includes(query.toLowerCase());
    const matchesSeverity = severity === "all" || log.severity === severity;
    const matchesType = eventType === "all" || log.event_type === eventType;
    return matchesQuery && matchesSeverity && matchesType;
  });

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-3">
        <label className="text-sm">
          <span className="mb-1 block text-slate-400">Search</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="w-full rounded-xl border border-white/10 bg-ink px-3 py-2"
            placeholder="Actor, address, message"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-slate-400">Severity</span>
          <select
            value={severity}
            onChange={(event) => setSeverity(event.target.value)}
            className="w-full rounded-xl border border-white/10 bg-ink px-3 py-2"
          >
            <option value="all">All</option>
            <option value="info">Info</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-slate-400">Event type</span>
          <select
            value={eventType}
            onChange={(event) => setEventType(event.target.value)}
            className="w-full rounded-xl border border-white/10 bg-ink px-3 py-2"
          >
            <option value="all">All</option>
            {types.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p className="text-sm text-slate-400">
        Showing {visible.length} of {logs.length}. Selected rows stay selected when filtered.
      </p>
      <div className="overflow-x-auto rounded-2xl border border-white/10">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-400">
            <tr>
              <th className="px-3 py-3 font-medium">Time</th>
              <th className="px-3 py-3 font-medium">Event</th>
              <th className="px-3 py-3 font-medium">Actor</th>
              <th className="px-3 py-3 font-medium">Source</th>
              <th className="px-3 py-3 font-medium">Message</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((log) => {
              const active = selected.includes(log.id);
              return (
                <tr key={log.id} className="border-t border-white/10">
                  <td className="px-3 py-3 font-mono text-xs">{log.timestamp}</td>
                  <td className="px-3 py-3">
                    {log.event_type}
                    <span className="mt-1 block text-xs text-slate-500">{log.severity}</span>
                  </td>
                  <td className="px-3 py-3">
                    {log.actor}
                    <span className="mt-1 block text-xs text-slate-500">
                      {log.ip} / {log.location}
                    </span>
                  </td>
                  <td className="px-3 py-3">{log.source}</td>
                  <td className="px-3 py-3">
                    <button
                      type="button"
                      aria-pressed={active}
                      className={signalClass(active)}
                      onClick={() => onToggle(log.id)}
                    >
                      {log.message}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
