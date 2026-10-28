from fastapi import APIRouter, Depends, Request

from app.api.dependencies.services import get_authenticate_user, get_current_user, get_register_user
from app.api.presenters import render
from app.application.use_cases.auth import AuthenticateUser, RegisterUser, build_profile
from app.domain.entities.user import User
from app.infrastructure.rate_limit import rate_limiter
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


def _client_host(request: Request) -> str:
    if request.client is None:
        return "unknown"
    return request.client.host


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(
    body: RegisterRequest,
    request: Request,
    use_case: RegisterUser = Depends(get_register_user),
) -> AuthResponse:
    rate_limiter.check(f"register:{_client_host(request)}", limit=5, window_seconds=60)
    result = use_case.execute(
        email=body.email,
        username=body.username,
        display_name=body.display_name,
        password=body.password,
    )
    return AuthResponse(access_token=result.access_token, user=render(UserResponse, result.user))


@router.post("/login", response_model=AuthResponse)
def login(
    body: LoginRequest,
    request: Request,
    use_case: AuthenticateUser = Depends(get_authenticate_user),
) -> AuthResponse:
    rate_limiter.check(f"login:{_client_host(request)}", limit=10, window_seconds=60)
    result = use_case.execute(email=body.email, password=body.password)
    return AuthResponse(access_token=result.access_token, user=render(UserResponse, result.user))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return render(UserResponse, build_profile(current_user))
