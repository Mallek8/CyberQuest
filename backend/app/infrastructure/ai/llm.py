import logging

import httpx

from app.domain.interfaces.hint_provider import HintDraft, HintProvider, MissionHintContext

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a cybersecurity tutor inside a training game. "
    "Give one short hint for the current level. "
    "Use the tutor note as the boundary of what you may say. "
    "You may explain the defensive concept in plain language. "
    "Do not list the correct rows, signal ids, or a full solution. "
    "Do not invent logs, links, or infrastructure. "
    "Keep the reply under 80 words."
)


class LlmHintProvider:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        fallback: HintProvider,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._url = f"{base_url.rstrip('/')}/chat/completions"
        self._model = model
        self._fallback = fallback
        self._transport = transport

    async def generate_hint(
        self,
        mission_context: MissionHintContext,
        hint_level: int,
    ) -> HintDraft:
        fallback = await self._fallback.generate_hint(mission_context, hint_level)
        try:
            content = await self._complete(mission_context)
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            logger.warning("LLM hint request failed. Using the curated hint.")
            return fallback
        cleaned = content.strip()
        if not cleaned:
            return fallback
        return HintDraft(content=cleaned[:600], provider="llm")

    async def _complete(self, mission_context: MissionHintContext) -> str:
        payload = {
            "model": self._model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Mission: {mission_context.mission_title}\n"
                        f"Category: {mission_context.category}\n"
                        f"Hint level: {mission_context.hint_level}\n"
                        f"Brief: {mission_context.briefing}\n"
                        f"Tutor note: {mission_context.tutor_note}"
                    ),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(transport=self._transport, timeout=8.0) as client:
            response = await client.post(self._url, json=payload, headers=headers)
            response.raise_for_status()
            return _read_content(response.json())


def _read_content(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return ""
    message = choices[0].get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    return content if isinstance(content, str) else ""
