from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserProgress:
    id: str
    user_id: str
    mission_id: str
    status: str
    best_score: int
    attempts_count: int
    completed_at: datetime | None
    updated_at: datetime


@dataclass
class Attempt:
    id: str
    user_id: str
    mission_id: str
    challenge_id: str
    selected_ids: list[str]
    score: int
    max_score: int
    passed: bool
    xp_awarded: int
    feedback: list[dict[str, str]]
    created_at: datetime
