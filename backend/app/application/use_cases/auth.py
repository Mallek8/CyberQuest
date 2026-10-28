from datetime import datetime
from uuid import uuid4

from app.application.results import AchievementView, AuthResult, UserProfile
from app.application.services.achievements import AchievementEvaluator
from app.application.services.level import XP_PER_LEVEL, level_for_xp, xp_into_level
from app.application.services.snapshot import PlayerSnapshotService
from app.core.clock import utc_now
from app.domain.entities.achievement import Achievement
from app.domain.entities.user import User
from app.domain.errors import ConflictError, UnauthorizedError
from app.domain.interfaces.repositories import AchievementRepository, UserRepository
from app.domain.interfaces.security import PasswordHasher, TokenProvider


def build_profile(user: User) -> UserProfile:
    return UserProfile(
        id=user.id,
        email=user.email,
        username=user.username,
        display_name=user.display_name,
        xp=user.xp,
        level=level_for_xp(user.xp),
        xp_into_level=xp_into_level(user.xp),
        xp_per_level=XP_PER_LEVEL,
        created_at=user.created_at,
    )


def achievement_view(achievement: Achievement, unlocked_at: datetime | None = None) -> AchievementView:
    return AchievementView(
        slug=achievement.slug,
        name=achievement.name,
        description=achievement.description,
        icon=achievement.icon,
        unlocked=unlocked_at is not None,
        unlocked_at=unlocked_at,
    )


class RegisterUser:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenProvider,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def execute(
        self,
        *,
        email: str,
        username: str,
        display_name: str,
        password: str,
    ) -> AuthResult:
        if self._users.get_by_email(email) is not None:
            raise ConflictError("An account with this email already exists.")
        if self._users.get_by_username(username) is not None:
            raise ConflictError("This username is already taken.")
        now = utc_now()
        user = User(
            id=str(uuid4()),
            email=email,
            username=username,
            hashed_password=self._hasher.hash_password(password),
            display_name=display_name,
            xp=0,
            created_at=now,
            updated_at=now,
        )
        self._users.add(user)
        return AuthResult(access_token=self._tokens.create_access_token(user.id), user=build_profile(user))


class AuthenticateUser:
    def __init__(self, users: UserRepository, hasher: PasswordHasher, tokens: TokenProvider) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def execute(self, *, email: str, password: str) -> AuthResult:
        user = self._users.get_by_email(email)
        password_hash = user.hashed_password if user else None
        if user is None or not self._hasher.verify_password(password, password_hash):
            raise UnauthorizedError("Email or password is incorrect.")
        return AuthResult(access_token=self._tokens.create_access_token(user.id), user=build_profile(user))


class GetProfile:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: str) -> UserProfile:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError("Authentication required.")
        return build_profile(user)


class AwardAchievements:
    def __init__(
        self,
        achievements: AchievementRepository,
        snapshots: PlayerSnapshotService,
        evaluator: AchievementEvaluator | None = None,
    ) -> None:
        self._achievements = achievements
        self._snapshots = snapshots
        self._evaluator = evaluator or AchievementEvaluator()

    def execute(self, user_id: str) -> list[AchievementView]:
        snapshot = self._snapshots.build(user_id)
        unlocked = self._achievements.unlocked_ids(user_id)
        earned = self._evaluator.newly_unlocked(
            snapshot,
            self._achievements.list_all(),
            unlocked,
        )
        views: list[AchievementView] = []
        for item in earned:
            granted = self._achievements.grant(user_id, item)
            views.append(achievement_view(item, granted.unlocked_at))
        return views
