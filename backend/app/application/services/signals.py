from app.domain.errors import InvalidSubmissionError


def extract_signals(payload: dict) -> list[dict[str, str]]:
    if "indicators" in payload:
        rows = payload["indicators"]
        return [_signal(item["id"], item.get("label") or item["id"]) for item in rows]
    if "logs" in payload:
        return [
            _signal(item["id"], f"{item['event_type']}: {item['actor']}") for item in payload["logs"]
        ]
    if "events" in payload:
        return [
            _signal(item["id"], f"{item['metric']} at {item['time']}") for item in payload["events"]
        ]
    raise InvalidSubmissionError("This mission has no signals to score.")


def signal_ids(payload: dict) -> list[str]:
    return [item["id"] for item in extract_signals(payload)]


def _signal(signal_id: str, label: str) -> dict[str, str]:
    return {"id": str(signal_id), "label": str(label)}
