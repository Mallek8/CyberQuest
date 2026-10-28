import type { AnomalyEvent, EmailContent, Indicator, LogEvent } from "../../types/api";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export function readEmail(payload: Record<string, unknown>): {
  email: EmailContent;
  indicators: Indicator[];
} | null {
  if (!isRecord(payload.email) || !Array.isArray(payload.indicators)) {
    return null;
  }
  return {
    email: payload.email as EmailContent,
    indicators: payload.indicators as Indicator[],
  };
}

export function readLogs(payload: Record<string, unknown>): LogEvent[] | null {
  if (!Array.isArray(payload.logs)) return null;
  return payload.logs as LogEvent[];
}

export function readEvents(payload: Record<string, unknown>): AnomalyEvent[] | null {
  if (!Array.isArray(payload.events)) return null;
  return payload.events as AnomalyEvent[];
}
