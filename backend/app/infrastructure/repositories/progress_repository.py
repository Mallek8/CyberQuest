from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.entities.progress import UserProgress
from app.infrastructure.database.models import UserProgressModel
from app.infrastructure.repositories.mappers import to_progress


class SqlAlchemyProgressRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, user_id: str, mission_id: str) -> UserProgress | None:
        row = self._session.scalar(
            select(UserProgressModel).where(
                UserProgressModel.user_id == user_id,
                UserProgressModel.mission_id == mission_id,
            )
        )
        return to_progress(row) if row else None

    def list_for_user(self, user_id: str) -> list[UserProgress]:
        rows = self._session.scalars(
            select(UserProgressModel).where(UserProgressModel.user_id == user_id)
        ).all()
        return [to_progress(row) for row in rows]

    def save(self, progress: UserProgress) -> UserProgress:
        row = self._session.scalar(
            select(UserProgressModel).where(
                UserProgressModel.user_id == progress.user_id,
                UserProgressModel.mission_id == progress.mission_id,
            )
        )
        if row is None:
            row = UserProgressModel(
                id=progress.id,
                user_id=progress.user_id,
                mission_id=progress.mission_id,
                status=progress.status,
                best_score=progress.best_score,
                attempts_count=progress.attempts_count,
                completed_at=progress.completed_at,
                updated_at=progress.updated_at,
            )
            try:
                with self._session.begin_nested():
                    self._session.add(row)
                    self._session.flush()
            except IntegrityError:
                row = self._session.scalar(
                    select(UserProgressModel).where(
                        UserProgressModel.user_id == progress.user_id,
                        UserProgressModel.mission_id == progress.mission_id,
                    )
                )
                if row is None:
                    raise
                _apply_progress(row, progress)
        else:
            _apply_progress(row, progress)
        self._session.flush()
        return to_progress(row)


def _apply_progress(row: UserProgressModel, progress: UserProgress) -> None:
    row.status = progress.status
    row.best_score = progress.best_score
    row.attempts_count = progress.attempts_count
    row.completed_at = progress.completed_at
    row.updated_at = progress.updated_at
