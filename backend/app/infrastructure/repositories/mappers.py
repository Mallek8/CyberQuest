from datetime import UTC, datetime

from app.domain.entities.achievement import Achievement, UserAchievement
from app.domain.entities.hint import HintRecord
from app.domain.entities.mission import Challenge, Mission
from app.domain.entities.progress import Attempt, UserProgress
from app.domain.entities.user import User
from app.infrastructure.database.models import (
    AchievementModel,
    AttemptModel,
    ChallengeModel,
    HintRequestModel,
    MissionModel,
    UserAchievementModel,
    UserModel,
    UserProgressModel,
)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def to_user(row: UserModel) -> User:
    return User(
        id=row.id,
        email=row.email,
        username=row.username,
        hashed_password=row.hashed_password,
        display_name=row.display_name,
        xp=row.xp,
        created_at=ensure_utc(row.created_at),
        updated_at=ensure_utc(row.updated_at),
    )


def to_mission(row: MissionModel) -> Mission:
    return Mission(
        id=row.id,
        slug=row.slug,
        title=row.title,
        description=row.description,
        briefing=row.briefing,
        category=row.category,
        difficulty=row.difficulty,
        xp_reward=row.xp_reward,
        pass_score=row.pass_score,
        order_index=row.order_index,
    )


def to_challenge(row: ChallengeModel) -> Challenge:
    return Challenge(
        id=row.id,
        mission_id=row.mission_id,
        prompt=row.prompt,
        challenge_type=row.challenge_type,
        payload=row.payload,
        answer_key=row.answer_key,
        hints=row.hints,
        max_score=row.max_score,
        order_index=row.order_index,
    )


def to_progress(row: UserProgressModel) -> UserProgress:
    completed = ensure_utc(row.completed_at) if row.completed_at else None
    return UserProgress(
        id=row.id,
        user_id=row.user_id,
        mission_id=row.mission_id,
        status=row.status,
        best_score=row.best_score,
        attempts_count=row.attempts_count,
        completed_at=completed,
        updated_at=ensure_utc(row.updated_at),
    )


def to_attempt(row: AttemptModel) -> Attempt:
    return Attempt(
        id=row.id,
        user_id=row.user_id,
        mission_id=row.mission_id,
        challenge_id=row.challenge_id,
        selected_ids=list(row.selected_ids),
        score=row.score,
        max_score=row.max_score,
        passed=row.passed,
        xp_awarded=row.xp_awarded,
        feedback=list(row.feedback),
        created_at=ensure_utc(row.created_at),
    )


def to_achievement(row: AchievementModel) -> Achievement:
    return Achievement(
        id=row.id,
        slug=row.slug,
        name=row.name,
        description=row.description,
        icon=row.icon,
        criteria=row.criteria,
    )


def to_user_achievement(row: UserAchievementModel, achievement: AchievementModel) -> UserAchievement:
    return UserAchievement(
        id=row.id,
        user_id=row.user_id,
        achievement_id=row.achievement_id,
        unlocked_at=ensure_utc(row.unlocked_at),
        achievement=to_achievement(achievement),
    )


def to_hint(row: HintRequestModel) -> HintRecord:
    return HintRecord(
        id=row.id,
        user_id=row.user_id,
        mission_id=row.mission_id,
        hint_level=row.hint_level,
        content=row.content,
        provider=row.provider,
        created_at=ensure_utc(row.created_at),
    )
