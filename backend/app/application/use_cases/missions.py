from uuid import uuid4

from app.application.results import (
    FeedbackView,
    MissionDetailView,
    MissionSummaryView,
    PublicChallengeView,
    SubmitView,
)
from app.application.services.access import (
    COMPLETED,
    IN_PROGRESS,
    MissionAccessPolicy,
    resolve_status,
)
from app.application.services.level import potential_xp
from app.application.services.scoring import score_challenge
from app.application.services.signals import extract_signals
from app.application.use_cases.auth import AwardAchievements, build_profile
from app.core.clock import utc_now
from app.domain.entities.mission import Mission
from app.domain.entities.progress import Attempt, UserProgress
from app.domain.errors import ForbiddenError, NotFoundError
from app.domain.interfaces.repositories import (
    AttemptRepository,
    MissionRepository,
    ProgressRepository,
    UserRepository,
)


class MissionCatalog:
    def __init__(
        self,
        missions: MissionRepository,
        progress: ProgressRepository,
        policy: MissionAccessPolicy | None = None,
    ) -> None:
        self._missions = missions
        self._progress = progress
        self._policy = policy or MissionAccessPolicy()

    def summaries(self, user_id: str | None) -> list[MissionSummaryView]:
        missions = self._missions.list_all()
        progress_rows = self._progress.list_for_user(user_id) if user_id else []
        by_mission = {row.mission_id: row for row in progress_rows}
        completed_orders = {
            mission.order_index
            for mission in missions
            if (row := by_mission.get(mission.id)) is not None and row.status == COMPLETED
        }
        return [
            self._summary(mission, by_mission.get(mission.id), completed_orders) for mission in missions
        ]

    def require_playable(self, user_id: str, slug: str) -> tuple[Mission, set[int]]:
        mission = self._missions.get_by_slug(slug)
        if mission is None:
            raise NotFoundError("Mission not found.")
        completed_orders = self._completed_orders(user_id)
        if not self._policy.can_play(mission.order_index, completed_orders):
            raise ForbiddenError("Complete the previous mission before playing this one.")
        return mission, completed_orders

    def _completed_orders(self, user_id: str) -> set[int]:
        missions = {item.id: item for item in self._missions.list_all()}
        completed: set[int] = set()
        for row in self._progress.list_for_user(user_id):
            mission = missions.get(row.mission_id)
            if mission is not None and row.status == COMPLETED:
                completed.add(mission.order_index)
        return completed

    def _summary(
        self,
        mission: Mission,
        progress: UserProgress | None,
        completed_orders: set[int],
    ) -> MissionSummaryView:
        attempts = progress.attempts_count if progress else 0
        status = resolve_status(
            mission.order_index,
            progress.status if progress else None,
            attempts,
            completed_orders,
            self._policy,
        )
        best_score = progress.best_score if progress and attempts else None
        return MissionSummaryView(
            slug=mission.slug,
            title=mission.title,
            description=mission.description,
            category=mission.category,
            difficulty=mission.difficulty,
            xp_reward=mission.xp_reward,
            pass_score=mission.pass_score,
            order_index=mission.order_index,
            status=status,
            best_score=best_score,
            attempts_count=attempts,
        )


class ListMissions:
    def __init__(self, catalog: MissionCatalog) -> None:
        self._catalog = catalog

    def execute(self, user_id: str | None) -> list[MissionSummaryView]:
        return self._catalog.summaries(user_id)


class GetMissionDetail:
    def __init__(self, catalog: MissionCatalog, missions: MissionRepository) -> None:
        self._catalog = catalog
        self._missions = missions

    def execute(self, user_id: str, slug: str) -> MissionDetailView:
        mission, completed_orders = self._catalog.require_playable(user_id, slug)
        challenge = self._missions.get_challenge(mission.id)
        if challenge is None:
            raise NotFoundError("This mission has no challenge.")
        progress = self._progress_for(user_id, mission.id)
        summary = self._catalog._summary(mission, progress, completed_orders)
        return MissionDetailView(
            **summary.__dict__,
            briefing=mission.briefing,
            challenge=PublicChallengeView(
                id=challenge.id,
                prompt=challenge.prompt,
                challenge_type=challenge.challenge_type,
                payload=challenge.payload,
            ),
        )

    def _progress_for(self, user_id: str, mission_id: str) -> UserProgress | None:
        return self._catalog._progress.get(user_id, mission_id)


class StartMission:
    def __init__(self, catalog: MissionCatalog, progress: ProgressRepository) -> None:
        self._catalog = catalog
        self._progress = progress

    def execute(self, user_id: str, slug: str) -> MissionSummaryView:
        mission, completed_orders = self._catalog.require_playable(user_id, slug)
        progress = self._progress.get(user_id, mission.id)
        now = utc_now()
        if progress is None:
            progress = UserProgress(
                id=str(uuid4()),
                user_id=user_id,
                mission_id=mission.id,
                status=IN_PROGRESS,
                best_score=0,
                attempts_count=0,
                completed_at=None,
                updated_at=now,
            )
        elif progress.status != COMPLETED:
            progress.status = IN_PROGRESS
            progress.updated_at = now
        saved = self._progress.save(progress)
        return self._catalog._summary(mission, saved, completed_orders)


class SubmitMission:
    def __init__(
        self,
        catalog: MissionCatalog,
        missions: MissionRepository,
        progress: ProgressRepository,
        attempts: AttemptRepository,
        users: UserRepository,
        awards: AwardAchievements,
    ) -> None:
        self._catalog = catalog
        self._missions = missions
        self._progress = progress
        self._attempts = attempts
        self._users = users
        self._awards = awards

    def execute(self, user_id: str, slug: str, selected_ids: list[str]) -> SubmitView:
        mission, _completed = self._catalog.require_playable(user_id, slug)
        challenge = self._missions.get_challenge(mission.id)
        if challenge is None:
            raise NotFoundError("This mission has no challenge.")
        signals = extract_signals(challenge.payload)
        breakdown = score_challenge(
            challenge_type=challenge.challenge_type,
            selected_ids=selected_ids,
            signals=signals,
            suspicious_ids=set(challenge.suspicious_ids),
            explanations=challenge.explanations,
            pass_score=mission.pass_score,
            max_score=challenge.max_score,
        )
        xp_awarded = 0
        if breakdown.passed:
            banked = self._attempts.xp_banked(user_id, mission.id)
            xp_awarded = max(
                0,
                potential_xp(mission.xp_reward, breakdown.score, breakdown.max_score) - banked,
            )
        now = utc_now()
        feedback = [
            {
                "id": item.id,
                "label": item.label,
                "outcome": item.outcome,
                "explanation": item.explanation,
            }
            for item in breakdown.feedback
        ]
        self._attempts.add(
            Attempt(
                id=str(uuid4()),
                user_id=user_id,
                mission_id=mission.id,
                challenge_id=challenge.id,
                selected_ids=list(dict.fromkeys(selected_ids)),
                score=breakdown.score,
                max_score=breakdown.max_score,
                passed=breakdown.passed,
                xp_awarded=xp_awarded,
                feedback=feedback,
                created_at=now,
            )
        )
        progress = self._progress.get(user_id, mission.id)
        if progress is None:
            progress = UserProgress(
                id=str(uuid4()),
                user_id=user_id,
                mission_id=mission.id,
                status=IN_PROGRESS,
                best_score=0,
                attempts_count=0,
                completed_at=None,
                updated_at=now,
            )
        if progress.attempts_count == 0:
            progress.best_score = breakdown.score
        else:
            progress.best_score = max(progress.best_score, breakdown.score)
        progress.attempts_count += 1
        progress.updated_at = now
        if breakdown.passed:
            progress.status = COMPLETED
            if progress.completed_at is None:
                progress.completed_at = now
        elif progress.status != COMPLETED:
            progress.status = IN_PROGRESS
        self._progress.save(progress)
        user = self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        if xp_awarded:
            user = self._users.add_xp(user_id, xp_awarded)
        profile = build_profile(user)
        unlocked = self._awards.execute(user_id)
        return SubmitView(
            score=breakdown.score,
            max_score=breakdown.max_score,
            passed=breakdown.passed,
            xp_awarded=xp_awarded,
            total_xp=profile.xp,
            level=profile.level,
            xp_into_level=profile.xp_into_level,
            xp_per_level=profile.xp_per_level,
            summary=breakdown.summary,
            feedback=[
                FeedbackView(
                    id=item.id,
                    label=item.label,
                    outcome=item.outcome,
                    explanation=item.explanation,
                )
                for item in breakdown.feedback
            ],
            newly_unlocked_achievements=unlocked,
            mission_status=progress.status,
        )
