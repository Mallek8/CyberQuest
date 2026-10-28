from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.hint import HintRecord
from app.infrastructure.database.models import HintRequestModel
from app.infrastructure.repositories.mappers import to_hint


class SqlAlchemyHintRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, hint: HintRecord) -> HintRecord:
        row = HintRequestModel(
            id=hint.id,
            user_id=hint.user_id,
            mission_id=hint.mission_id,
            hint_level=hint.hint_level,
            content=hint.content,
            provider=hint.provider,
            created_at=hint.created_at,
        )
        self._session.add(row)
        self._session.flush()
        return to_hint(row)

    def list_for_mission(self, user_id: str, mission_id: str) -> list[HintRecord]:
        rows = self._session.scalars(
            select(HintRequestModel)
            .where(
                HintRequestModel.user_id == user_id,
                HintRequestModel.mission_id == mission_id,
            )
            .order_by(HintRequestModel.hint_level)
        ).all()
        return [to_hint(row) for row in rows]

    def count_for_user(self, user_id: str) -> int:
        total = self._session.scalar(
            select(func.count())
            .select_from(HintRequestModel)
            .where(HintRequestModel.user_id == user_id)
        )
        return int(total or 0)
