import math
from dataclasses import dataclass

from app.domain.errors import InvalidSubmissionError


@dataclass(frozen=True)
class FeedbackItem:
    id: str
    label: str
    outcome: str
    explanation: str


@dataclass(frozen=True)
class ScoreBreakdown:
    score: int
    max_score: int
    passed: bool
    true_positives: int
    false_positives: int
    false_negatives: int
    summary: str
    feedback: list[FeedbackItem]


class SignalSelectionScorer:
    """Score a set selection with an F1-style balance of hits and noise."""

    def score(
        self,
        *,
        selected_ids: list[str],
        signals: list[dict[str, str]],
        suspicious_ids: set[str],
        explanations: dict[str, str],
        pass_score: int,
        max_score: int = 100,
    ) -> ScoreBreakdown:
        known = {item["id"] for item in signals}
        if not suspicious_ids.issubset(known):
            raise InvalidSubmissionError("This mission is missing part of its answer key.")

        selected: list[str] = []
        seen: set[str] = set()
        for signal_id in selected_ids:
            if signal_id not in known:
                raise InvalidSubmissionError(f"Unknown signal: {signal_id}.")
            if signal_id not in seen:
                seen.add(signal_id)
                selected.append(signal_id)

        selected_set = set(selected)
        hits = [signal_id for signal_id in selected if signal_id in suspicious_ids]
        false_alarms = [signal_id for signal_id in selected if signal_id not in suspicious_ids]
        missed = [item["id"] for item in signals if item["id"] in suspicious_ids - selected_set]

        precision = _ratio(len(hits), len(hits) + len(false_alarms))
        recall = _ratio(len(hits), len(hits) + len(missed))
        f1 = 0.0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)
        score = int(math.floor((f1 * max_score) + 0.5))

        labels = {item["id"]: item["label"] for item in signals}
        feedback: list[FeedbackItem] = []
        for signal_id in hits:
            feedback.append(
                _item(signal_id, labels, explanations, "hit"),
            )
        for signal_id in false_alarms:
            feedback.append(
                _item(signal_id, labels, explanations, "false_alarm"),
            )
        for signal_id in missed:
            feedback.append(
                _item(signal_id, labels, explanations, "missed"),
            )

        return ScoreBreakdown(
            score=score,
            max_score=max_score,
            passed=score >= pass_score,
            true_positives=len(hits),
            false_positives=len(false_alarms),
            false_negatives=len(missed),
            summary=_summary(len(hits), len(false_alarms), len(missed), score >= pass_score),
            feedback=feedback,
        )


SCORERS: dict[str, SignalSelectionScorer] = {
    "select_signals": SignalSelectionScorer(),
}


def score_challenge(
    *,
    challenge_type: str,
    selected_ids: list[str],
    signals: list[dict[str, str]],
    suspicious_ids: set[str],
    explanations: dict[str, str],
    pass_score: int,
    max_score: int,
) -> ScoreBreakdown:
    scorer = SCORERS.get(challenge_type)
    if scorer is None:
        raise InvalidSubmissionError("This challenge type is not supported.")
    return scorer.score(
        selected_ids=selected_ids,
        signals=signals,
        suspicious_ids=suspicious_ids,
        explanations=explanations,
        pass_score=pass_score,
        max_score=max_score,
    )


def _item(
    signal_id: str,
    labels: dict[str, str],
    explanations: dict[str, str],
    outcome: str,
) -> FeedbackItem:
    return FeedbackItem(
        id=signal_id,
        label=labels.get(signal_id, signal_id),
        outcome=outcome,
        explanation=explanations.get(signal_id, "No explanation was recorded for this signal."),
    )


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _count(noun: str, value: int) -> str:
    if value == 1:
        return f"1 {noun}"
    return f"{value} {noun}s"


def _summary(hits: int, false_alarms: int, missed: int, passed: bool) -> str:
    text = (
        f"You confirmed {_count('suspicious signal', hits)}, "
        f"flagged {_count('benign item', false_alarms)}, "
        f"and missed {_count('signal', missed)}."
    )
    if passed:
        return text + " This clears the mission."
    return text + " The score is below the pass mark. Adjust the selection and submit again."
