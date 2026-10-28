export function formatWhen(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function statusLabel(status: string): string {
  if (status === "locked") return "Locked";
  if (status === "available") return "Ready";
  if (status === "in_progress") return "In progress";
  if (status === "completed") return "Cleared";
  return status;
}

export function categoryLabel(category: string): string {
  if (category === "phishing") return "Phishing";
  if (category === "logs") return "Log analysis";
  if (category === "anomaly") return "Anomaly detection";
  return category;
}

export function titleCase(value: string): string {
  if (!value) return value;
  return value.charAt(0).toUpperCase() + value.slice(1);
}
