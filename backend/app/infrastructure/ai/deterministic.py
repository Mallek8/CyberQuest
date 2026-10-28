from app.domain.interfaces.hint_provider import HintDraft, MissionHintContext


class DeterministicHintProvider:
    async def generate_hint(
        self,
        mission_context: MissionHintContext,
        hint_level: int,
    ) -> HintDraft:
        del hint_level
        return HintDraft(content=mission_context.tutor_note.strip(), provider="deterministic")
