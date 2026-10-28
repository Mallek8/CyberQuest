from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.mission import Mission
from app.domain.entities.progress import Attempt
from app.infrastructure.database.models import AttemptModel, MissionModel
from app.infrastructure.repositories.mappers import to_attempt, to_mission


class SqlAlchemyAttemptRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, attempt: Attempt) -> Attempt:
        row = AttemptModel(
            id=attempt.id,
            user_id=attempt.user_id,
            mission_id=attempt.mission_id,
            challenge_id=attempt.challenge_id,
            selected_ids=attempt.selected_ids,
            score=attempt.score,
            max_score=attempt.max_score,
            passed=attempt.passed,
            xp_awarded=attempt.xp_awarded,
            feedback=attempt.feedback,
            created_at=attempt.created_at,
        )
        self._session.add(row)
        self._session.flush()
        return to_attempt(row)

    def xp_banked(self, user_id: str, mission_id: str) -> int:
        total = self._session.scalar(
            select(func.coalesce(func.sum(AttemptModel.xp_awarded), 0)).where(
                AttemptModel.user_id == user_id,
                AttemptModel.mission_id == mission_id,
            )
        )
        return int(total or 0)

    def count_for_user(self, user_id: str) -> int:
        total = self._session.scalar(
            select(func.count()).select_from(AttemptModel).where(AttemptModel.user_id == user_id)
        )
        return int(total or 0)

    def count_perfect_for_user(self, user_id: str) -> int:
        total = self._session.scalar(
            select(func.count())
            .select_from(AttemptModel)
            .where(
                AttemptModel.user_id == user_id,
                AttemptModel.score == AttemptModel.max_score,
                AttemptModel.max_score > 0,
            )
        )
        return int(total or 0)

    def list_recent_for_user(self, user_id: str, limit: int) -> list[tuple[Attempt, Mission]]:
        rows = self._session.execute(
            select(AttemptModel, MissionModel)
            .join(MissionModel, AttemptModel.mission_id == MissionModel.id)
            .where(AttemptModel.user_id == user_id)
            .order_by(AttemptModel.created_at.desc())
            .limit(limit)
        ).all()
        return [(to_attempt(attempt), to_mission(mission)) for attempt, mission in rows]
