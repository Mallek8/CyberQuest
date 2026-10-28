import {
  Activity,
  BadgeCheck,
  MailWarning,
  NotebookPen,
  ScrollText,
  Shield,
  Sparkles,
  Target,
  type LucideIcon,
} from "lucide-react";

const ICONS: Record<string, LucideIcon> = {
  shield: Shield,
  "mail-warning": MailWarning,
  "scroll-text": ScrollText,
  activity: Activity,
  "badge-check": BadgeCheck,
  target: Target,
  sparkles: Sparkles,
  "notebook-pen": NotebookPen,
};

export function AchievementIcon({ name }: { name: string }) {
  const Icon = ICONS[name] ?? Shield;
  return <Icon className="h-5 w-5" aria-hidden="true" />;
}
