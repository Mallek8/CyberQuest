from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.mission import Challenge, Mission
from app.infrastructure.database.models import ChallengeModel, MissionModel
from app.infrastructure.repositories.mappers import to_challenge, to_mission


class SqlAlchemyMissionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Mission]:
        rows = self._session.scalars(select(MissionModel).order_by(MissionModel.order_index)).all()
        return [to_mission(row) for row in rows]

    def get_by_slug(self, slug: str) -> Mission | None:
        row = self._session.scalar(select(MissionModel).where(MissionModel.slug == slug))
        return to_mission(row) if row else None

    def get_challenge(self, mission_id: str) -> Challenge | None:
        row = self._session.scalar(
            select(ChallengeModel)
            .where(ChallengeModel.mission_id == mission_id)
            .order_by(ChallengeModel.order_index)
        )
        return to_challenge(row) if row else None
