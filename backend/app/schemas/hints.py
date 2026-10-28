from datetime import datetime

from pydantic import BaseModel

from app.schemas.missions import AchievementResponse


class StoredHintResponse(BaseModel):
    hint_level: int
    content: str
    provider: str
    created_at: datetime


class HintResponse(BaseModel):
    hint_level: int
    content: str
    hints_used: int
    hints_remaining: int
    provider: str
    newly_unlocked_achievements: list[AchievementResponse]


class HintHistoryResponse(BaseModel):
    hints: list[StoredHintResponse]
    hints_used: int
    hints_remaining: int
