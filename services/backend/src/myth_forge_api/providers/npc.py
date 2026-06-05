from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Protocol

from pydantic import BaseModel

from myth_forge_api.domain.models import (
    ContextCapsule,
    GeneratedAsset,
    MythSeed,
    NPCDirectorResult,
    NPCReaction,
    ObjectCard,
)

if TYPE_CHECKING:
    from myth_forge_api.config import Settings

EXPECTED_NPC_IDS = {"mara", "ior", "senn"}
EXPECTED_NPC_ID_LIST = ["mara", "ior", "senn"]


class NPCDirector(Protocol):
    provider_name: str

    def validate_configuration(self) -> None:
        ...

    def generate_reactions(
        self,
        session_id: str,
        object_card: ObjectCard,
        myth_seed: MythSeed,
        context_capsule: ContextCapsule,
        generated_asset: GeneratedAsset,
    ) -> NPCDirectorResult:
        ...


class LocalNPCDirector:
    provider_name = "local_stub"

    def validate_configuration(self) -> None:
        return None

    def generate_reactions(
        self,
        session_id: str,
        object_card: ObjectCard,
        myth_seed: MythSeed,
        context_capsule: ContextCapsule,
        generated_asset: GeneratedAsset,
    ) -> NPCDirectorResult:
        return NPCDirectorResult(
            provider=self.provider_name,
            reactions=[
                NPCReaction(
                    npc_id="mara",
                    name="Mara",
                    emotion="awe",
                    interpretation=f"{object_card.label} is a sign that the village has been heard.",
                    plan=[
                        "approach_artifact",
                        "kneel_near_artifact",
                        "invite_neighbors_to_witness",
                    ],
                    world_change="faith_in_player_increases",
                ),
                NPCReaction(
                    npc_id="ior",
                    name="Ior",
                    emotion="suspicion",
                    interpretation=f"{myth_seed.title} may be a test rather than a gift.",
                    plan=[
                        "keep_distance",
                        "question_mara",
                        "propose_guarding_the_artifact_overnight",
                    ],
                    world_change="village_debate_starts",
                ),
                NPCReaction(
                    npc_id="senn",
                    name="Senn",
                    emotion="curiosity",
                    interpretation="The artifact should be named before anyone tries to use it.",
                    plan=[
                        "circle_artifact",
                        "sketch_symbol_in_dirt",
                        "suggest_ritual_name",
                    ],
                    world_change="artifact_gets_a_local_name",
                ),
            ],
        )


class OpenAINPCProviderError(RuntimeError):
    pass


class OpenAINPCConfigurationError(OpenAINPCProviderError):
    pass


class OpenAINPCOutput(BaseModel):
    reactions: list[NPCReaction]


class OpenAINPCDirector:
    provider_name = "openai"

    def __init__(
        self,
        api_key: str | None,
        model: str,
        api_base_url: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.api_base_url = api_base_url
        self.client = client

    @classmethod
    def from_settings(cls, settings: Settings) -> OpenAINPCDirector:
        return cls(
            api_key=settings.openai_api_key,
            model=settings.openai_npc_model,
            api_base_url=settings.openai_api_base_url,
        )

    def validate_configuration(self) -> None:
        if not self.api_key:
            raise OpenAINPCConfigurationError("OPENAI_API_KEY is required for NPC generation.")

    def generate_reactions(
        self,
        session_id: str,
        object_card: ObjectCard,
        myth_seed: MythSeed,
        context_capsule: ContextCapsule,
        generated_asset: GeneratedAsset,
    ) -> NPCDirectorResult:
        self.validate_configuration()

        client = self.client or self._build_client()
        try:
            response = client.responses.parse(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You direct three text-only NPCs for Personal Myth Forge. "
                            "Use only approved personal context summaries. Raw private data, "
                            "messages, calendar text, and contact details are not available."
                        ),
                    },
                    {
                        "role": "user",
                        "content": _npc_director_prompt(
                            session_id=session_id,
                            object_card=object_card,
                            myth_seed=myth_seed,
                            context_capsule=context_capsule,
                            generated_asset=generated_asset,
                        ),
                    },
                ],
                text_format=OpenAINPCOutput,
            )
            output = OpenAINPCOutput.model_validate(response.output_parsed)
        except OpenAINPCProviderError:
            raise
        except Exception as exc:
            message = _sanitize_provider_error(exc, secret=self.api_key)
            raise OpenAINPCProviderError(f"OpenAI NPC generation failed: {message}") from exc

        npc_ids = {reaction.npc_id for reaction in output.reactions}
        if len(output.reactions) != 3 or npc_ids != EXPECTED_NPC_IDS:
            expected = ", ".join(EXPECTED_NPC_ID_LIST)
            raise OpenAINPCProviderError(f"OpenAI NPC response must include exactly: {expected}.")

        return NPCDirectorResult(provider=self.provider_name, reactions=output.reactions)

    def _build_client(self) -> Any:
        from openai import OpenAI

        kwargs: dict[str, str] = {"api_key": self.api_key or ""}
        if self.api_base_url:
            kwargs["base_url"] = self.api_base_url
        return OpenAI(**kwargs)


def _npc_director_prompt(
    session_id: str,
    object_card: ObjectCard,
    myth_seed: MythSeed,
    context_capsule: ContextCapsule,
    generated_asset: GeneratedAsset,
) -> str:
    return (
        f"Session: {session_id}\n"
        f"Object label: {object_card.label}\n"
        f"Materials: {', '.join(object_card.materials) or 'unknown'}\n"
        f"Symbolic reading: {object_card.symbolic_reading}\n"
        f"Myth title: {myth_seed.title}\n"
        f"Personal resonance summary: {myth_seed.personal_resonance}\n"
        f"Approved current theme capsule: {context_capsule.current_theme}\n"
        f"Approved desired tone capsule: {context_capsule.desired_tone}\n"
        f"Generated asset URI: {generated_asset.uri}\n"
        "Return exactly three reactions for NPC ids mara, ior, and senn. "
        "Each plan item must be a safe visible action, not a purchase, print order, "
        "private-data request, or destructive act."
    )


def _sanitize_provider_error(exc: Exception, secret: str | None = None) -> str:
    message = str(exc)
    if secret:
        message = message.replace(secret, "[redacted]")
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._:-]+",
        r"Bearer\s+[A-Za-z0-9._:-]+",
        r"raw=[^\s,;]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;]+",
    ]
    for pattern in replacements:
        message = re.sub(pattern, "[redacted]", message, flags=re.IGNORECASE)
    return message
