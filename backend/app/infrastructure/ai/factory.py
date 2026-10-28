from app.core.config import Settings
from app.domain.interfaces.hint_provider import HintProvider
from app.infrastructure.ai.deterministic import DeterministicHintProvider
from app.infrastructure.ai.llm import LlmHintProvider


def build_hint_provider(settings: Settings) -> HintProvider:
    curated = DeterministicHintProvider()
    if settings.ai_provider.lower() == "llm" and settings.llm_api_key:
        return LlmHintProvider(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            fallback=curated,
        )
    return curated
