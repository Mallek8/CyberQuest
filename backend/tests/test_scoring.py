import pytest
from app.application.services.scoring import score_challenge
from app.domain.errors import InvalidSubmissionError

SIGNALS = [
    {"id": "a", "label": "A"},
    {"id": "b", "label": "B"},
    {"id": "c", "label": "C"},
    {"id": "d", "label": "D"},
]
SUSPICIOUS = {"a", "b", "c"}
EXPLANATIONS = {item["id"]: f"why {item['id']}" for item in SIGNALS}


def _score(selected: list[str]):
    return score_challenge(
        challenge_type="select_signals",
        selected_ids=selected,
        signals=SIGNALS,
        suspicious_ids=SUSPICIOUS,
        explanations=EXPLANATIONS,
        pass_score=70,
        max_score=100,
    )


def test_perfect_selection_scores_100():
    result = _score(["a", "b", "c"])
    assert result.score == 100
    assert result.passed is True
    assert result.false_positives == 0
    assert result.false_negatives == 0


def test_partial_recall_is_rounded_from_f1():
    result = _score(["a", "b"])
    assert result.true_positives == 2
    assert result.false_negatives == 1
    assert result.score == 80
    assert result.passed is True


def test_false_alarm_lowers_the_score():
    result = _score(["a", "d"])
    assert result.true_positives == 1
    assert result.false_positives == 1
    assert result.false_negatives == 2
    assert result.score == 40
    assert result.passed is False
    assert any(item.outcome == "false_alarm" for item in result.feedback)


def test_empty_selection_scores_zero():
    result = _score([])
    assert result.score == 0
    assert result.passed is False
    assert result.false_negatives == 3


def test_duplicate_ids_are_counted_once():
    result = _score(["a", "a", "b", "c"])
    assert result.score == 100


def test_unknown_signal_is_rejected():
    with pytest.raises(InvalidSubmissionError):
        _score(["missing"])


def test_unsupported_challenge_type_is_rejected():
    with pytest.raises(InvalidSubmissionError):
        score_challenge(
            challenge_type="shell",
            selected_ids=[],
            signals=SIGNALS,
            suspicious_ids=SUSPICIOUS,
            explanations=EXPLANATIONS,
            pass_score=70,
            max_score=100,
        )
