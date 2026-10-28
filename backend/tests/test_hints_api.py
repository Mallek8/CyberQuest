from app.api.dependencies.services import get_hint_provider
from app.domain.interfaces.hint_provider import HintDraft
from app.infrastructure.database.catalog import CATALOG
from app.main import app
from tests.helpers import register


def _first_hint() -> str:
    mission = next(item for item in CATALOG if item["slug"] == "phishing-investigation")
    return next(item["text"] for item in mission["challenge"]["hints"] if item["level"] == 1)


def test_curated_hints_stop_at_three(client):
    headers = register(client)
    contents = []
    for level in range(1, 4):
        response = client.post("/api/v1/missions/phishing-investigation/hints", headers=headers)
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["hint_level"] == level
        assert body["provider"] == "deterministic"
        assert body["hints_remaining"] == 3 - level
        contents.append(body["content"])
        assert "sender-domain" not in body["content"]
    assert contents[0] == _first_hint()
    blocked = client.post("/api/v1/missions/phishing-investigation/hints", headers=headers)
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "hint_limit"
    history = client.get("/api/v1/missions/phishing-investigation/hints", headers=headers)
    assert len(history.json()["hints"]) == 3
    badges = client.get("/api/v1/achievements", headers=headers)
    assert any(item["slug"] == "second-opinion" and item["unlocked"] for item in badges.json())


def test_hint_output_that_names_a_signal_is_replaced(client):
    class LeakyProvider:
        async def generate_hint(self, mission_context, hint_level):
            del mission_context, hint_level
            return HintDraft(content="The correct row is sender-domain.", provider="llm")

    app.dependency_overrides[get_hint_provider] = lambda: LeakyProvider()
    headers = register(client, username="lin", email="lin@example.com")
    response = client.post("/api/v1/missions/phishing-investigation/hints", headers=headers)
    assert response.status_code == 201, response.text
    body = response.json()
    assert "sender-domain" not in body["content"]
    assert body["content"] == _first_hint()
    assert body["provider"] == "deterministic"
