from app.infrastructure.database.catalog import CATALOG
from tests.helpers import register


def _suspicious(slug: str) -> list[str]:
    mission = next(item for item in CATALOG if item["slug"] == slug)
    return list(mission["challenge"]["answer_key"]["suspicious_ids"])


def _submit(client, headers, slug: str, selected: list[str] | None = None):
    response = client.post(
        f"/api/v1/missions/{slug}/submit",
        headers=headers,
        json={"selected_ids": _suspicious(slug) if selected is None else selected},
    )
    return response


def test_mission_list_hides_locked_scenarios_and_answer_keys(client):
    public = client.get("/api/v1/missions")
    assert public.status_code == 200
    body = public.json()
    assert [item["slug"] for item in body] == [
        "phishing-investigation",
        "security-log-analysis",
        "anomaly-detection",
    ]
    assert body[0]["status"] == "available"
    assert body[1]["status"] == "locked"
    assert "answer_key" not in public.text
    assert "suspicious_ids" not in public.text

    headers = register(client)
    detail = client.get("/api/v1/missions/phishing-investigation", headers=headers)
    assert detail.status_code == 200
    assert "suspicious_ids" not in detail.text
    assert "answer_key" not in detail.text
    assert "display name does not establish identity" not in detail.text
    locked = client.get("/api/v1/missions/security-log-analysis", headers=headers)
    assert locked.status_code == 403
    assert locked.json()["error"]["code"] == "forbidden"


def test_server_scores_phishing_and_does_not_farm_xp(client):
    headers = register(client)
    first = _submit(
        client,
        headers,
        "phishing-investigation",
        [
            "sender-domain",
            "reply-to-mismatch",
            "auth-results",
            "urgency",
            "credential-request",
        ],
    )
    assert first.status_code == 200, first.text
    assert first.json()["score"] == 83
    assert first.json()["passed"] is True
    assert first.json()["xp_awarded"] == 99
    slugs = {item["slug"] for item in first.json()["newly_unlocked_achievements"]}
    assert "phish-hunter" in slugs
    assert "sharp-eye" not in slugs

    perfect = _submit(client, headers, "phishing-investigation")
    assert perfect.status_code == 200
    assert perfect.json()["score"] == 100
    assert perfect.json()["xp_awarded"] == 21
    assert perfect.json()["total_xp"] == 120
    assert any(item["outcome"] == "hit" for item in perfect.json()["feedback"])
    assert "display name does not establish identity" in perfect.text

    replay = _submit(client, headers, "phishing-investigation")
    assert replay.json()["xp_awarded"] == 0
    assert replay.json()["total_xp"] == 120
    assert {item["slug"] for item in replay.json()["newly_unlocked_achievements"]} == {"field-notes"}


def test_unknown_signal_and_locked_submit(client):
    headers = register(client)
    bad = _submit(client, headers, "phishing-investigation", ["not-a-signal"])
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "invalid_submission"
    locked = _submit(client, headers, "anomaly-detection")
    assert locked.status_code == 403


def test_full_playthrough_unlocks_case_closed(client):
    headers = register(client, username="grace", email="grace@example.com")
    unlocked = set()
    for slug in ("phishing-investigation", "security-log-analysis", "anomaly-detection"):
        response = _submit(client, headers, slug)
        assert response.status_code == 200, response.text
        assert response.json()["passed"] is True
        assert response.json()["score"] == 100
        unlocked.update(item["slug"] for item in response.json()["newly_unlocked_achievements"])
    assert "case-closed" in unlocked
    assert "log-reader" in unlocked
    assert "signal-spotter" in unlocked

    dashboard = client.get("/api/v1/progress/dashboard", headers=headers)
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["completed_missions"] == 3
    assert body["next_mission"] is None
    assert body["user"]["xp"] == 120 + 160 + 200

    achievements = client.get("/api/v1/achievements", headers=headers)
    earned = [item["slug"] for item in achievements.json() if item["unlocked"]]
    assert "case-closed" in earned

    attempts = client.get("/api/v1/progress/attempts", headers=headers)
    assert attempts.status_code == 200
    assert len(attempts.json()) == 3


def test_security_headers_and_openapi(client):
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.headers["x-content-type-options"] == "nosniff"
    assert health.headers["x-frame-options"] == "DENY"
    schema = client.get("/openapi.json")
    assert schema.status_code == 200
    paths = schema.json()["paths"]
    assert "/api/v1/missions/{slug}/submit" in paths
    assert "/api/v1/auth/register" in paths
