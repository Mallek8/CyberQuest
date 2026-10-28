from fastapi import APIRouter, Depends, Query

from app.api.dependencies.services import get_current_user, get_dashboard, get_list_attempts
from app.api.presenters import render
from app.application.use_cases.progress import GetDashboard, ListAttempts
from app.domain.entities.user import User
from app.schemas.missions import AttemptResponse, DashboardResponse

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    use_case: GetDashboard = Depends(get_dashboard),
    user: User = Depends(get_current_user),
) -> DashboardResponse:
    return render(DashboardResponse, use_case.execute(user.id))


@router.get("/attempts", response_model=list[AttemptResponse])
def attempts(
    use_case: ListAttempts = Depends(get_list_attempts),
    user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=50),
) -> list[AttemptResponse]:
    return [render(AttemptResponse, item) for item in use_case.execute(user.id, limit)]
