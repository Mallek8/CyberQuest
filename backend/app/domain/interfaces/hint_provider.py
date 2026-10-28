from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MissionHintContext:
    mission_title: str
    category: str
    briefing: str
    tutor_note: str
    hint_level: int


@dataclass(frozen=True)
class HintDraft:
    content: str
    provider: str


class HintProvider(Protocol):
    async def generate_hint(
        self,
        mission_context: MissionHintContext,
        hint_level: int,
    ) -> HintDraft: ...
