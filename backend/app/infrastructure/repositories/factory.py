from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.infrastructure.repositories.achievement_repository import SqlAlchemyAchievementRepository
from app.infrastructure.repositories.attempt_repository import SqlAlchemyAttemptRepository
from app.infrastructure.repositories.hint_repository import SqlAlchemyHintRepository
from app.infrastructure.repositories.mission_repository import SqlAlchemyMissionRepository
from app.infrastructure.repositories.progress_repository import SqlAlchemyProgressRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


@dataclass
class Repositories:
    users: SqlAlchemyUserRepository
    missions: SqlAlchemyMissionRepository
    progress: SqlAlchemyProgressRepository
    attempts: SqlAlchemyAttemptRepository
    achievements: SqlAlchemyAchievementRepository
    hints: SqlAlchemyHintRepository


def build_repositories(session: Session) -> Repositories:
    return Repositories(
        users=SqlAlchemyUserRepository(session),
        missions=SqlAlchemyMissionRepository(session),
        progress=SqlAlchemyProgressRepository(session),
        attempts=SqlAlchemyAttemptRepository(session),
        achievements=SqlAlchemyAchievementRepository(session),
        hints=SqlAlchemyHintRepository(session),
    )
