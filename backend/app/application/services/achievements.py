from dataclasses import dataclass
from typing import Protocol

from app.domain.entities.achievement import Achievement


@dataclass(frozen=True)
class PlayerSnapshot:
    completed_slugs: set[str]
    completed_missions: int
    perfect_scores: int
    hint_count: int
    total_attempts: int
    total_missions: int


class AchievementRule(Protocol):
    def is_met(self, snapshot: PlayerSnapshot) -> bool: ...


class MissionsCompletedRule:
    def __init__(self, count: int) -> None:
        self._count = count

    def is_met(self, snapshot: PlayerSnapshot) -> bool:
        return snapshot.completed_missions >= self._count


class MissionSlugRule:
    def __init__(self, slug: str) -> None:
        self._slug = slug

    def is_met(self, snapshot: PlayerSnapshot) -> bool:
        return self._slug in snapshot.completed_slugs


class PerfectScoreRule:
    def __init__(self, count: int) -> None:
        self._count = count

    def is_met(self, snapshot: PlayerSnapshot) -> bool:
        return snapshot.perfect_scores >= self._count


class HintsUsedRule:
    def __init__(self, count: int) -> None:
        self._count = count

    def is_met(self, snapshot: PlayerSnapshot) -> bool:
        return snapshot.hint_count >= self._count


class AttemptsRule:
    def __init__(self, count: int) -> None:
        self._count = count

    def is_met(self, snapshot: PlayerSnapshot) -> bool:
        return snapshot.total_attempts >= self._count


class NeverRule:
    def is_met(self, snapshot: PlayerSnapshot) -> bool:
        return False


def build_rule(criteria: dict) -> AchievementRule:
    rule_type = criteria.get("type")
    if rule_type == "missions_completed":
        return MissionsCompletedRule(int(criteria["count"]))
    if rule_type == "mission_slug":
        return MissionSlugRule(str(criteria["slug"]))
    if rule_type == "perfect_score":
        return PerfectScoreRule(int(criteria.get("count", 1)))
    if rule_type == "hints_used":
        return HintsUsedRule(int(criteria["count"]))
    if rule_type == "attempts":
        return AttemptsRule(int(criteria["count"]))
    return NeverRule()


class AchievementEvaluator:
    def newly_unlocked(
        self,
        snapshot: PlayerSnapshot,
        definitions: list[Achievement],
        unlocked_ids: set[str],
    ) -> list[Achievement]:
        earned: list[Achievement] = []
        for definition in definitions:
            if definition.id in unlocked_ids:
                continue
            if build_rule(definition.criteria).is_met(snapshot):
                earned.append(definition)
        return earned
