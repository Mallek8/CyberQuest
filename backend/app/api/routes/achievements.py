from fastapi import APIRouter, Depends

from app.api.dependencies.services import get_current_user, get_list_achievements
from app.api.presenters import render
from app.application.use_cases.progress import ListAchievements
from app.domain.entities.user import User
from app.schemas.missions import AchievementResponse

router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("", response_model=list[AchievementResponse])
def list_achievements(
    use_case: ListAchievements = Depends(get_list_achievements),
    user: User = Depends(get_current_user),
) -> list[AchievementResponse]:
    return [render(AchievementResponse, item) for item in use_case.execute(user.id)]
