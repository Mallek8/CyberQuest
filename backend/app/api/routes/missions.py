from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.dependencies.services import (
    get_current_user,
    get_list_missions,
    get_mission_detail,
    get_optional_user,
    get_start_mission,
    get_submit_mission,
)
from app.api.presenters import render
from app.application.use_cases.missions import (
    GetMissionDetail,
    ListMissions,
    StartMission,
    SubmitMission,
)
from app.domain.entities.user import User
from app.schemas.missions import (
    MissionDetailResponse,
    MissionSummaryResponse,
    SubmitRequest,
    SubmitResponse,
)

router = APIRouter(prefix="/missions", tags=["Missions"])
Slug = Annotated[str, Path(pattern=r"^[a-z0-9-]{1,80}$")]


@router.get("", response_model=list[MissionSummaryResponse])
def list_missions(
    use_case: ListMissions = Depends(get_list_missions),
    user: User | None = Depends(get_optional_user),
) -> list[MissionSummaryResponse]:
    user_id = user.id if user else None
    return [render(MissionSummaryResponse, item) for item in use_case.execute(user_id)]


@router.get("/{slug}", response_model=MissionDetailResponse)
def mission_detail(
    slug: Slug,
    use_case: GetMissionDetail = Depends(get_mission_detail),
    user: User = Depends(get_current_user),
) -> MissionDetailResponse:
    return render(MissionDetailResponse, use_case.execute(user.id, slug))


@router.post("/{slug}/start", response_model=MissionSummaryResponse)
def start_mission(
    slug: Slug,
    use_case: StartMission = Depends(get_start_mission),
    user: User = Depends(get_current_user),
) -> MissionSummaryResponse:
    return render(MissionSummaryResponse, use_case.execute(user.id, slug))


@router.post("/{slug}/submit", response_model=SubmitResponse)
def submit_mission(
    slug: Slug,
    body: SubmitRequest,
    use_case: SubmitMission = Depends(get_submit_mission),
    user: User = Depends(get_current_user),
) -> SubmitResponse:
    return render(SubmitResponse, use_case.execute(user.id, slug, body.selected_ids))
