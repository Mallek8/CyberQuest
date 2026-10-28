from uuid import uuid4

from app.application.results import HintHistoryView, HintView, StoredHintView
from app.application.services.hint_guard import contains_secret
from app.application.use_cases.auth import AwardAchievements
from app.application.use_cases.missions import MissionCatalog
from app.core.clock import utc_now
from app.domain.entities.hint import HintRecord
from app.domain.errors import HintLimitError, NotFoundError
from app.domain.interfaces.hint_provider import HintProvider, MissionHintContext
from app.domain.interfaces.repositories import HintRepository, MissionRepository


class RequestHint:
    def __init__(
        self,
        catalog: MissionCatalog,
        missions: MissionRepository,
        hints: HintRepository,
        provider: HintProvider,
        awards: AwardAchievements,
        hint_limit: int,
    ) -> None:
        self._catalog = catalog
        self._missions = missions
        self._hints = hints
        self._provider = provider
        self._awards = awards
        self._hint_limit = hint_limit

    async def execute(self, user_id: str, slug: str) -> HintView:
        mission, _completed = self._catalog.require_playable(user_id, slug)
        challenge = self._missions.get_challenge(mission.id)
        if challenge is None:
            raise NotFoundError("This mission has no challenge.")
        used = self._hints.list_for_mission(user_id, mission.id)
        available = min(self._hint_limit, len(challenge.hints))
        if len(used) >= available:
            raise HintLimitError("No hints left for this mission.")
        next_level = len(used) + 1
        tutor_note = _tutor_note(challenge.hints, next_level)
        draft = await self._provider.generate_hint(
            MissionHintContext(
                mission_title=mission.title,
                category=mission.category,
                briefing=mission.briefing,
                tutor_note=tutor_note,
                hint_level=next_level,
            ),
            next_level,
        )
        content = draft.content.strip() or tutor_note
        provider_name = draft.provider
        secret_ids = _all_signal_ids(challenge.payload) + challenge.suspicious_ids
        if contains_secret(content, secret_ids):
            content = tutor_note
            provider_name = "deterministic"
        self._hints.add(
            HintRecord(
                id=str(uuid4()),
                user_id=user_id,
                mission_id=mission.id,
                hint_level=next_level,
                content=content,
                provider=provider_name,
                created_at=utc_now(),
            )
        )
        unlocked = self._awards.execute(user_id)
        return HintView(
            hint_level=next_level,
            content=content,
            hints_used=len(used) + 1,
            hints_remaining=available - (len(used) + 1),
            provider=provider_name,
            newly_unlocked_achievements=unlocked,
        )


class ListHints:
    def __init__(
        self,
        catalog: MissionCatalog,
        missions: MissionRepository,
        hints: HintRepository,
        hint_limit: int,
    ) -> None:
        self._catalog = catalog
        self._missions = missions
        self._hints = hints
        self._hint_limit = hint_limit

    def execute(self, user_id: str, slug: str) -> HintHistoryView:
        mission, _completed = self._catalog.require_playable(user_id, slug)
        challenge = self._missions.get_challenge(mission.id)
        if challenge is None:
            raise NotFoundError("This mission has no challenge.")
        used = self._hints.list_for_mission(user_id, mission.id)
        available = min(self._hint_limit, len(challenge.hints))
        return HintHistoryView(
            hints=[
                StoredHintView(
                    hint_level=item.hint_level,
                    content=item.content,
                    provider=item.provider,
                    created_at=item.created_at,
                )
                for item in used
            ],
            hints_used=len(used),
            hints_remaining=max(0, available - len(used)),
        )


def _tutor_note(hints: list[dict], level: int) -> str:
    for item in hints:
        if int(item.get("level", 0)) == level:
            return str(item.get("text", "")).strip()
    raise HintLimitError("No hints left for this mission.")


def _all_signal_ids(payload: dict) -> list[str]:
    rows: list[dict] = []
    for key in ("indicators", "logs", "events"):
        value = payload.get(key)
        if isinstance(value, list):
            rows = value
            break
    return [str(item.get("id", "")) for item in rows if isinstance(item, dict)]
