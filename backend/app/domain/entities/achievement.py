from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Achievement:
    id: str
    slug: str
    name: str
    description: str
    icon: str
    criteria: dict[str, Any]


@dataclass
class UserAchievement:
    id: str
    user_id: str
    achievement_id: str
    unlocked_at: datetime
    achievement: Achievement
