from app.application.services.access import COMPLETED
from app.application.services.achievements import PlayerSnapshot
from app.domain.interfaces.repositories import (
    AttemptRepository,
    HintRepository,
    MissionRepository,
    ProgressRepository,
)


class PlayerSnapshotService:
    def __init__(
        self,
        missions: MissionRepository,
        progress: ProgressRepository,
        attempts: AttemptRepository,
        hints: HintRepository,
    ) -> None:
        self._missions = missions
        self._progress = progress
        self._attempts = attempts
        self._hints = hints

    def build(self, user_id: str) -> PlayerSnapshot:
        missions = {item.id: item for item in self._missions.list_all()}
        completed: set[str] = set()
        for row in self._progress.list_for_user(user_id):
            mission = missions.get(row.mission_id)
            if mission is not None and row.status == COMPLETED:
                completed.add(mission.slug)
        return PlayerSnapshot(
            completed_slugs=completed,
            completed_missions=len(completed),
            perfect_scores=self._attempts.count_perfect_for_user(user_id),
            hint_count=self._hints.count_for_user(user_id),
            total_attempts=self._attempts.count_for_user(user_id),
            total_missions=len(missions),
        )
