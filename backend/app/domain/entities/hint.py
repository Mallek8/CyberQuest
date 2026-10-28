from dataclasses import dataclass
from datetime import datetime


@dataclass
class HintRecord:
    id: str
    user_id: str
    mission_id: str
    hint_level: int
    content: str
    provider: str
    created_at: datetime
