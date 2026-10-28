from app.application.services.access import (
    AVAILABLE,
    COMPLETED,
    IN_PROGRESS,
    LOCKED,
    MissionAccessPolicy,
    resolve_status,
)
from app.application.services.achievements import (
    AchievementEvaluator,
    PlayerSnapshot,
    build_rule,
)
from app.application.services.hint_guard import contains_secret
from app.application.services.level import level_for_xp, potential_xp, xp_into_level
from app.domain.entities.achievement import Achievement


def test_missions_unlock_in_order():
    policy = MissionAccessPolicy()
    assert policy.can_play(1, set()) is True
    assert policy.can_play(2, set()) is False
    assert policy.can_play(2, {1}) is True
    assert policy.can_play(3, {1}) is False
    assert policy.can_play(3, {1, 2}) is True


def test_status_resolution():
    assert resolve_status(2, None, 0, set()) == LOCKED
    assert resolve_status(1, None, 0, set()) == AVAILABLE
    assert resolve_status(1, IN_PROGRESS, 0, set()) == IN_PROGRESS
    assert resolve_status(1, COMPLETED, 1, set()) == COMPLETED


def test_level_curve():
    assert level_for_xp(0) == 1
    assert xp_into_level(0) == 0
    assert level_for_xp(150) == 2
    assert xp_into_level(149) == 149
    assert potential_xp(120, 83, 100) == 99


def test_hint_guard_detects_signal_ids():
    assert contains_secret("Look at sender-domain now", ["sender-domain"]) is True
    assert contains_secret("Compare the sender domain", ["sender-domain"]) is False


def test_unknown_badge_rule_does_not_match():
    rule = build_rule({"type": "not-a-rule"})
    snapshot = PlayerSnapshot(set(), 3, 3, 3, 3, 3)
    assert rule.is_met(snapshot) is False


def test_evaluator_skips_badges_already_unlocked():
    achievement = Achievement(
        id="a1",
        slug="first-report",
        name="First Report",
        description="Clear one",
        icon="shield",
        criteria={"type": "missions_completed", "count": 1},
    )
    snapshot = PlayerSnapshot({"phishing-investigation"}, 1, 0, 0, 1, 3)
    evaluator = AchievementEvaluator()
    assert evaluator.newly_unlocked(snapshot, [achievement], set()) == [achievement]
    assert evaluator.newly_unlocked(snapshot, [achievement], {"a1"}) == []
