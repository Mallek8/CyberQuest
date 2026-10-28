import asyncio

import httpx
from app.domain.interfaces.hint_provider import MissionHintContext
from app.infrastructure.ai.deterministic import DeterministicHintProvider
from app.infrastructure.ai.llm import LlmHintProvider


def _context() -> MissionHintContext:
    return MissionHintContext(
        mission_title="Phishing Investigation",
        category="phishing",
        briefing="Company domain is northwind.example.",
        tutor_note="Compare the sender domain with the company domain.",
        hint_level=1,
    )


def test_deterministic_provider_returns_the_tutor_note():
    draft = asyncio.run(DeterministicHintProvider().generate_hint(_context(), 1))
    assert draft.provider == "deterministic"
    assert draft.content == "Compare the sender domain with the company domain."


def test_llm_provider_returns_model_text_without_putting_the_key_in_the_body():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = request.read().decode()
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Check who the message claims to be."}}]},
        )

    provider = LlmHintProvider(
        api_key="secret-key",
        base_url="https://llm.example/v1",
        model="demo",
        fallback=DeterministicHintProvider(),
        transport=httpx.MockTransport(handler),
    )
    draft = asyncio.run(provider.generate_hint(_context(), 1))
    assert draft.provider == "llm"
    assert draft.content == "Check who the message claims to be."
    assert seen["auth"] == "Bearer secret-key"
    assert "secret-key" not in seen["body"]
    assert "suspicious_ids" not in seen["body"]


def test_llm_provider_falls_back_when_the_request_fails():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "down"})

    provider = LlmHintProvider(
        api_key="secret-key",
        base_url="https://llm.example/v1",
        model="demo",
        fallback=DeterministicHintProvider(),
        transport=httpx.MockTransport(handler),
    )
    draft = asyncio.run(provider.generate_hint(_context(), 1))
    assert draft.provider == "deterministic"
    assert "company domain" in draft.content
