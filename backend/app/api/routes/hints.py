from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request

from app.api.dependencies.services import get_current_user, get_list_hints, get_request_hint
from app.api.presenters import render
from app.application.use_cases.hints import ListHints, RequestHint
from app.domain.entities.user import User
from app.infrastructure.rate_limit import rate_limiter
from app.schemas.hints import HintHistoryResponse, HintResponse

router = APIRouter(prefix="/missions", tags=["Hints"])
Slug = Annotated[str, Path(pattern=r"^[a-z0-9-]{1,80}$")]


def _client_host(request: Request) -> str:
    if request.client is None:
        return "unknown"
    return request.client.host


@router.get("/{slug}/hints", response_model=HintHistoryResponse)
def list_hints(
    slug: Slug,
    use_case: ListHints = Depends(get_list_hints),
    user: User = Depends(get_current_user),
) -> HintHistoryResponse:
    return render(HintHistoryResponse, use_case.execute(user.id, slug))


@router.post("/{slug}/hints", response_model=HintResponse, status_code=201)
async def request_hint(
    slug: Slug,
    request: Request,
    use_case: RequestHint = Depends(get_request_hint),
    user: User = Depends(get_current_user),
) -> HintResponse:
    rate_limiter.check(f"hint:{user.id}:{_client_host(request)}", limit=20, window_seconds=60)
    return render(HintResponse, await use_case.execute(user.id, slug))
