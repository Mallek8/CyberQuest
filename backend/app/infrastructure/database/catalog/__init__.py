import json

from app.application.services.hint_guard import contains_secret
from app.application.services.signals import signal_ids
from app.infrastructure.database.catalog.achievements import ACHIEVEMENTS
from app.infrastructure.database.catalog.anomaly import ANOMALY_MISSION
from app.infrastructure.database.catalog.logs import LOG_MISSION
from app.infrastructure.database.catalog.phishing import PHISHING_MISSION

CATALOG = [PHISHING_MISSION, LOG_MISSION, ANOMALY_MISSION]


def validate_catalog() -> None:
    slugs: set[str] = set()
    orders: set[int] = set()
    for mission in CATALOG:
        slug = mission["slug"]
        if slug in slugs:
            raise ValueError(f"Duplicate mission slug: {slug}")
        slugs.add(slug)
        order = mission["order_index"]
        if order in orders:
            raise ValueError(f"Duplicate mission order: {order}")
        orders.add(order)
        challenge = mission["challenge"]
        ids = signal_ids(challenge["payload"])
        if len(ids) != len(set(ids)):
            raise ValueError(f"{slug} has duplicate signal ids")
        suspicious = list(challenge["answer_key"]["suspicious_ids"])
        if not set(suspicious).issubset(ids):
            raise ValueError(f"{slug} answer key references an unknown signal")
        explanations = challenge["answer_key"]["explanations"]
        if set(explanations) != set(ids):
            raise ValueError(f"{slug} explanations must cover every signal")
        levels = [item["level"] for item in challenge["hints"]]
        if levels != [1, 2, 3]:
            raise ValueError(f"{slug} must define hint levels 1, 2, and 3")
        public_text = " ".join(
            [
                mission["description"],
                mission["briefing"],
                *(item["text"] for item in challenge["hints"]),
            ]
        )
        if contains_secret(public_text, ids):
            raise ValueError(f"{slug} public text contains a signal id")
        payload_text = json.dumps(challenge["payload"]).lower()
        for explanation in explanations.values():
            if explanation.lower() in payload_text:
                raise ValueError(f"{slug} payload repeats an answer explanation")
    achievement_slugs = [item["slug"] for item in ACHIEVEMENTS]
    if len(achievement_slugs) != len(set(achievement_slugs)):
        raise ValueError("Duplicate achievement slug")


validate_catalog()
