from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.services.snapshot import PlayerSnapshotService
from app.application.use_cases.auth import (
    AuthenticateUser,
    AwardAchievements,
    GetProfile,
    RegisterUser,
)
from app.application.use_cases.hints import ListHints, RequestHint
from app.application.use_cases.missions import (
    GetMissionDetail,
    ListMissions,
    MissionCatalog,
    StartMission,
    SubmitMission,
)
from app.application.use_cases.progress import GetDashboard, ListAchievements, ListAttempts
from app.core.config import get_settings
from app.domain.entities.user import User
from app.domain.errors import UnauthorizedError
from app.domain.interfaces.hint_provider import HintProvider
from app.domain.interfaces.security import PasswordHasher, TokenProvider
from app.infrastructure.ai.factory import build_hint_provider
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.factory import Repositories, build_repositories
from app.infrastructure.security.passwords import BcryptPasswordHasher
from app.infrastructure.security.tokens import JwtTokenProvider

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher(get_settings().bcrypt_rounds)


@lru_cache
def get_tokens() -> JwtTokenProvider:
    settings = get_settings()
    return JwtTokenProvider(
        settings.jwt_secret,
        settings.jwt_algorithm,
        settings.access_token_expire_minutes,
    )


def get_hint_provider() -> HintProvider:
    return build_hint_provider(get_settings())


def get_repos(db: Session = Depends(get_db)) -> Repositories:
    return build_repositories(db)


def get_catalog(repos: Repositories = Depends(get_repos)) -> MissionCatalog:
    return MissionCatalog(repos.missions, repos.progress)


def get_awards(repos: Repositories = Depends(get_repos)) -> AwardAchievements:
    return AwardAchievements(
        repos.achievements,
        PlayerSnapshotService(repos.missions, repos.progress, repos.attempts, repos.hints),
    )


def get_register_user(
    repos: Repositories = Depends(get_repos),
    hasher: PasswordHasher = Depends(get_hasher),
    tokens: TokenProvider = Depends(get_tokens),
) -> RegisterUser:
    return RegisterUser(repos.users, hasher, tokens)


def get_authenticate_user(
    repos: Repositories = Depends(get_repos),
    hasher: PasswordHasher = Depends(get_hasher),
    tokens: TokenProvider = Depends(get_tokens),
) -> AuthenticateUser:
    return AuthenticateUser(repos.users, hasher, tokens)


def get_profile_use_case(repos: Repositories = Depends(get_repos)) -> GetProfile:
    return GetProfile(repos.users)


def get_list_missions(catalog: MissionCatalog = Depends(get_catalog)) -> ListMissions:
    return ListMissions(catalog)


def get_mission_detail(
    catalog: MissionCatalog = Depends(get_catalog),
    repos: Repositories = Depends(get_repos),
) -> GetMissionDetail:
    return GetMissionDetail(catalog, repos.missions)


def get_start_mission(
    catalog: MissionCatalog = Depends(get_catalog),
    repos: Repositories = Depends(get_repos),
) -> StartMission:
    return StartMission(catalog, repos.progress)


def get_submit_mission(
    catalog: MissionCatalog = Depends(get_catalog),
    repos: Repositories = Depends(get_repos),
    awards: AwardAchievements = Depends(get_awards),
) -> SubmitMission:
    return SubmitMission(
        catalog,
        repos.missions,
        repos.progress,
        repos.attempts,
        repos.users,
        awards,
    )


def get_request_hint(
    catalog: MissionCatalog = Depends(get_catalog),
    repos: Repositories = Depends(get_repos),
    provider: HintProvider = Depends(get_hint_provider),
    awards: AwardAchievements = Depends(get_awards),
) -> RequestHint:
    return RequestHint(
        catalog,
        repos.missions,
        repos.hints,
        provider,
        awards,
        get_settings().hint_limit_per_mission,
    )


def get_list_hints(
    catalog: MissionCatalog = Depends(get_catalog),
    repos: Repositories = Depends(get_repos),
) -> ListHints:
    return ListHints(catalog, repos.missions, repos.hints, get_settings().hint_limit_per_mission)


def get_dashboard(
    catalog: MissionCatalog = Depends(get_catalog),
    repos: Repositories = Depends(get_repos),
) -> GetDashboard:
    return GetDashboard(repos.users, catalog, repos.achievements)


def get_list_attempts(repos: Repositories = Depends(get_repos)) -> ListAttempts:
    return ListAttempts(repos.attempts)


def get_list_achievements(repos: Repositories = Depends(get_repos)) -> ListAchievements:
    return ListAchievements(repos.achievements)


def _user_from_token(
    credentials: HTTPAuthorizationCredentials | None,
    repos: Repositories,
    tokens: TokenProvider,
    *,
    required: bool,
) -> User | None:
    if credentials is None:
        if required:
            raise UnauthorizedError("Authentication required.")
        return None
    if credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Authentication required.")
    user = repos.users.get_by_id(tokens.read_user_id(credentials.credentials))
    if user is None:
        raise UnauthorizedError("Authentication required.")
    return user


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    repos: Repositories = Depends(get_repos),
    tokens: TokenProvider = Depends(get_tokens),
) -> User:
    user = _user_from_token(credentials, repos, tokens, required=True)
    if user is None:
        raise UnauthorizedError("Authentication required.")
    return user


def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    repos: Repositories = Depends(get_repos),
    tokens: TokenProvider = Depends(get_tokens),
) -> User | None:
    return _user_from_token(credentials, repos, tokens, required=False)
