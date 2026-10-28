from dataclasses import dataclass
from typing import Any


@dataclass
class Mission:
    id: str
    slug: str
    title: str
    description: str
    briefing: str
    category: str
    difficulty: str
    xp_reward: int
    pass_score: int
    order_index: int


@dataclass
class Challenge:
    id: str
    mission_id: str
    prompt: str
    challenge_type: str
    payload: dict[str, Any]
    answer_key: dict[str, Any]
    hints: list[dict[str, Any]]
    max_score: int
    order_index: int

    @property
    def suspicious_ids(self) -> list[str]:
        raw = self.answer_key.get("suspicious_ids", [])
        return [str(item) for item in raw]

    @property
    def explanations(self) -> dict[str, str]:
        raw = self.answer_key.get("explanations", {})
        return {str(key): str(value) for key, value in raw.items()}
