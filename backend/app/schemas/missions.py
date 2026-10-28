import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.auth import UserResponse


class AchievementResponse(BaseModel):
    slug: str
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: datetime | None = None


class MissionSummaryResponse(BaseModel):
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


class ChallengeResponse(BaseModel):
    id: str
    prompt: str
    challenge_type: str
    payload: dict[str, Any]


class MissionDetailResponse(MissionSummaryResponse):
    briefing: str
    challenge: ChallengeResponse


class SubmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selected_ids: list[str] = Field(default_factory=list, max_length=40)

    @field_validator("selected_ids")
    @classmethod
    def check_ids(cls, value: list[str]) -> list[str]:
        for item in value:
            if not re.fullmatch(r"[a-z0-9-]{1,64}", item):
                raise ValueError("Signal ids use lowercase letters, numbers, and hyphens.")
        return value


class FeedbackResponse(BaseModel):
    id: str
    label: str
    outcome: str
    explanation: str


class SubmitResponse(BaseModel):
    score: int
    max_score: int
    passed: bool
    xp_awarded: int
    total_xp: int
    level: int
    xp_into_level: int
    xp_per_level: int
    summary: str
    feedback: list[FeedbackResponse]
    newly_unlocked_achievements: list[AchievementResponse]
    mission_status: str


class AttemptResponse(BaseModel):
    id: str
    mission_slug: str
    mission_title: str
    score: int
    max_score: int
    passed: bool
    xp_awarded: int
    created_at: datetime


class DashboardResponse(BaseModel):
    user: UserResponse
    completed_missions: int
    total_missions: int
    badges_earned: int
    total_badges: int
    next_mission: MissionSummaryResponse | None
    recent_achievements: list[AchievementResponse]
