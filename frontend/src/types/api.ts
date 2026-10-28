export type User = {
  id: string;
  email: string;
  username: string;
  display_name: string;
  xp: number;
  level: number;
  xp_into_level: number;
  xp_per_level: number;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type MissionStatus = "locked" | "available" | "in_progress" | "completed";

export type MissionSummary = {
  slug: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  xp_reward: number;
  pass_score: number;
  order_index: number;
  status: MissionStatus;
  best_score: number | null;
  attempts_count: number;
};

export type Challenge = {
  id: string;
  prompt: string;
  challenge_type: string;
  payload: Record<string, unknown>;
};

export type MissionDetail = MissionSummary & {
  briefing: string;
  challenge: Challenge;
};

export type Achievement = {
  slug: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlocked_at: string | null;
};

export type FeedbackItem = {
  id: string;
  label: string;
  outcome: "hit" | "false_alarm" | "missed";
  explanation: string;
};

export type SubmitResult = {
  score: number;
  max_score: number;
  passed: boolean;
  xp_awarded: number;
  total_xp: number;
  level: number;
  xp_into_level: number;
  xp_per_level: number;
  summary: string;
  feedback: FeedbackItem[];
  newly_unlocked_achievements: Achievement[];
  mission_status: string;
};

export type HintRecord = {
  hint_level: number;
  content: string;
  provider: string;
  created_at: string;
};

export type HintHistory = {
  hints: HintRecord[];
  hints_used: number;
  hints_remaining: number;
};

export type HintResult = {
  hint_level: number;
  content: string;
  hints_used: number;
  hints_remaining: number;
  provider: string;
  newly_unlocked_achievements: Achievement[];
};

export type DashboardData = {
  user: User;
  completed_missions: number;
  total_missions: number;
  badges_earned: number;
  total_badges: number;
  next_mission: MissionSummary | null;
  recent_achievements: Achievement[];
};

export type AttemptRecord = {
  id: string;
  mission_slug: string;
  mission_title: string;
  score: number;
  max_score: number;
  passed: boolean;
  xp_awarded: number;
  created_at: string;
};

export type Indicator = {
  id: string;
  label: string;
  detail: string;
  group: string;
};

export type EmailContent = {
  from_name: string;
  from_address: string;
  reply_to: string;
  subject: string;
  date: string;
  body: string;
  headers: { name: string; value: string }[];
};

export type LogEvent = {
  id: string;
  timestamp: string;
  source: string;
  event_type: string;
  actor: string;
  ip: string;
  location: string;
  severity: string;
  message: string;
};

export type AnomalyEvent = {
  id: string;
  time: string;
  metric: string;
  value: number;
  baseline: number;
  unit: string;
  context: string;
};
