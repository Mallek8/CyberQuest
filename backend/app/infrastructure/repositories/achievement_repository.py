from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import utc_now
from app.domain.entities.achievement import Achievement, UserAchievement
from app.infrastructure.database.models import AchievementModel, UserAchievementModel
from app.infrastructure.repositories.mappers import to_achievement, to_user_achievement


class SqlAlchemyAchievementRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Achievement]:
        rows = self._session.scalars(select(AchievementModel).order_by(AchievementModel.name)).all()
        return [to_achievement(row) for row in rows]

    def unlocked_ids(self, user_id: str) -> set[str]:
        rows = self._session.scalars(
            select(UserAchievementModel.achievement_id).where(UserAchievementModel.user_id == user_id)
        ).all()
        return set(rows)

    def list_for_user(self, user_id: str) -> list[UserAchievement]:
        rows = self._session.execute(
            select(UserAchievementModel, AchievementModel)
            .join(AchievementModel, UserAchievementModel.achievement_id == AchievementModel.id)
            .where(UserAchievementModel.user_id == user_id)
            .order_by(UserAchievementModel.unlocked_at.desc())
        ).all()
        return [to_user_achievement(link, achievement) for link, achievement in rows]

    def grant(self, user_id: str, achievement: Achievement) -> UserAchievement:
        row = UserAchievementModel(
            id=str(uuid4()),
            user_id=user_id,
            achievement_id=achievement.id,
            unlocked_at=utc_now(),
        )
        self._session.add(row)
        self._session.flush()
        stored = self._session.get(AchievementModel, achievement.id)
        if stored is None:
            raise RuntimeError("Achievement disappeared during grant.")
        return to_user_achievement(row, stored)
