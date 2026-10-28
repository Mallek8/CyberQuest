from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import utc_now
from app.infrastructure.database.catalog import ACHIEVEMENTS, CATALOG
from app.infrastructure.database.models import AchievementModel, ChallengeModel, MissionModel


def seed_catalog(session: Session) -> None:
    now = utc_now()
    for item in CATALOG:
        mission = session.scalar(select(MissionModel).where(MissionModel.slug == item["slug"]))
        if mission is None:
            mission = MissionModel(id=str(uuid4()), slug=item["slug"], created_at=now)
            session.add(mission)
        mission.title = item["title"]
        mission.description = item["description"]
        mission.briefing = item["briefing"]
        mission.category = item["category"]
        mission.difficulty = item["difficulty"]
        mission.xp_reward = item["xp_reward"]
        mission.pass_score = item["pass_score"]
        mission.order_index = item["order_index"]
        session.flush()

        challenge_data = item["challenge"]
        challenge = session.scalar(
            select(ChallengeModel)
            .where(ChallengeModel.mission_id == mission.id)
            .order_by(ChallengeModel.order_index)
        )
        if challenge is None:
            challenge = ChallengeModel(id=str(uuid4()), mission_id=mission.id, created_at=now)
            session.add(challenge)
        challenge.prompt = challenge_data["prompt"]
        challenge.challenge_type = challenge_data["challenge_type"]
        challenge.payload = challenge_data["payload"]
        challenge.answer_key = challenge_data["answer_key"]
        challenge.hints = challenge_data["hints"]
        challenge.max_score = challenge_data["max_score"]
        challenge.order_index = 1

    for item in ACHIEVEMENTS:
        achievement = session.scalar(
            select(AchievementModel).where(AchievementModel.slug == item["slug"])
        )
        if achievement is None:
            achievement = AchievementModel(id=str(uuid4()), slug=item["slug"], created_at=now)
            session.add(achievement)
        achievement.name = item["name"]
        achievement.description = item["description"]
        achievement.icon = item["icon"]
        achievement.criteria = item["criteria"]
    session.flush()


def main() -> None:
    from app.infrastructure.database.session import SessionLocal

    session = SessionLocal()
    try:
        seed_catalog(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
