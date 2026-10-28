from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserProfile:
    id: str
    email: str
    username: str
    display_name: str
    xp: int
    level: int
    xp_into_level: int
    xp_per_level: int
    created_at: datetime


@dataclass
class AchievementView:
    slug: str
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: datetime | None


@dataclass
class MissionSummaryView:
    slug: str
    title: str
    description: str
    category: str
    difficulty: str
    xp_reward: int
    pass_score: int
    order_index: int
    status: str
    best_score: int | None
    attempts_count: int


@dataclass
class PublicChallengeView:
    id: str
    prompt: str
    challenge_type: str
    payload: dict


@dataclass
class MissionDetailView:
    slug: str
    title: str
    description: str
    category: str
    difficulty: str
    xp_reward: int
    pass_score: int
    order_index: int
    status: str
    best_score: int | None
    attempts_count: int
    briefing: str
    challenge: PublicChallengeView


@dataclass
class FeedbackView:
    id: str
    label: str
    outcome: str
    explanation: str


@dataclass
class SubmitView:
    score: int
    max_score: int
    passed: bool
    xp_awarded: int
    total_xp: int
    level: int
    xp_into_level: int
    xp_per_level: int
    summary: str
    feedback: list[FeedbackView]
    newly_unlocked_achievements: list[AchievementView]
    mission_status: str


@dataclass
class StoredHintView:
    hint_level: int
    content: str
    provider: str
    created_at: datetime


@dataclass
class HintView:
    hint_level: int
    content: str
    hints_used: int
    hints_remaining: int
    provider: str
    newly_unlocked_achievements: list[AchievementView]


@dataclass
class HintHistoryView:
    hints: list[StoredHintView]
    hints_used: int
    hints_remaining: int


@dataclass
class AttemptView:
    id: str
    mission_slug: str
    mission_title: str
    score: int
    max_score: int
    passed: bool
    xp_awarded: int
    created_at: datetime


@dataclass
class DashboardView:
    user: UserProfile
    completed_missions: int
    total_missions: int
    badges_earned: int
    total_badges: int
    next_mission: MissionSummaryView | None
    recent_achievements: list[AchievementView]


@dataclass
class AuthResult:
    access_token: str
    user: UserProfile
