from app.application.results import AchievementView, AttemptView, DashboardView
from app.application.services.access import recommend_mission
from app.application.use_cases.auth import achievement_view, build_profile
from app.application.use_cases.missions import MissionCatalog
from app.domain.errors import UnauthorizedError
from app.domain.interfaces.repositories import (
    AchievementRepository,
    AttemptRepository,
    UserRepository,
)


class GetDashboard:
    def __init__(
        self,
        users: UserRepository,
        catalog: MissionCatalog,
        achievements: AchievementRepository,
    ) -> None:
        self._users = users
        self._catalog = catalog
        self._achievements = achievements

    def execute(self, user_id: str) -> DashboardView:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError("Authentication required.")
        summaries = self._catalog.summaries(user_id)
        earned = self._achievements.list_for_user(user_id)
        recent = [
            achievement_view(item.achievement, item.unlocked_at) for item in earned[:4]
        ]
        completed = sum(1 for item in summaries if item.status == "completed")
        return DashboardView(
            user=build_profile(user),
            completed_missions=completed,
            total_missions=len(summaries),
            badges_earned=len(earned),
            total_badges=len(self._achievements.list_all()),
            next_mission=recommend_mission(summaries),
            recent_achievements=recent,
        )


class ListAttempts:
    def __init__(self, attempts: AttemptRepository) -> None:
        self._attempts = attempts

    def execute(self, user_id: str, limit: int = 20) -> list[AttemptView]:
        rows = self._attempts.list_recent_for_user(user_id, limit)
        return [
            AttemptView(
                id=attempt.id,
                mission_slug=mission.slug,
                mission_title=mission.title,
                score=attempt.score,
                max_score=attempt.max_score,
                passed=attempt.passed,
                xp_awarded=attempt.xp_awarded,
                created_at=attempt.created_at,
            )
            for attempt, mission in rows
        ]


class ListAchievements:
    def __init__(self, achievements: AchievementRepository) -> None:
        self._achievements = achievements

    def execute(self, user_id: str) -> list[AchievementView]:
        earned = {item.achievement_id: item.unlocked_at for item in self._achievements.list_for_user(user_id)}
        views = [
            achievement_view(item, earned.get(item.id)) for item in self._achievements.list_all()
        ]
        return sorted(views, key=lambda item: (not item.unlocked, item.name))
