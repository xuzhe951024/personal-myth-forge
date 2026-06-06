from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Protocol

from pydantic import BaseModel, Field

from myth_forge_api.domain.models import (
    ContextCapsule,
    GeneratedAsset,
    MythSeed,
    NPCAgentTrace,
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
        agent_traces = _local_agent_traces(object_card=object_card, myth_seed=myth_seed)
        return NPCDirectorResult(
            provider=self.provider_name,
            agent_runtime="local_agent_runtime",
            agent_traces=agent_traces,
            reactions=_local_reactions_from_traces(agent_traces, myth_seed=myth_seed),
        )


class OpenAINPCProviderError(RuntimeError):
    pass


class OpenAINPCConfigurationError(OpenAINPCProviderError):
    pass


class OpenAINPCOutput(BaseModel):
    reactions: list[NPCReaction]
    agent_traces: list[NPCAgentTrace] = Field(default_factory=list)


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
        agent_traces = _validated_agent_traces(output.agent_traces, output.reactions)
        trace_ids = {trace.npc_id for trace in agent_traces}
        if len(agent_traces) != 3 or trace_ids != EXPECTED_NPC_IDS:
            expected = ", ".join(EXPECTED_NPC_ID_LIST)
            raise OpenAINPCProviderError(f"OpenAI NPC traces must include exactly: {expected}.")

        return NPCDirectorResult(
            provider=self.provider_name,
            reactions=output.reactions,
            agent_runtime="openai_structured_runtime",
            agent_traces=agent_traces,
        )

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
        "Also return one agent trace per NPC with belief, intention, proposed_action, "
        "rationale, and confidence. Each agent trace should include a brief NPC "
        "rationale without revealing raw personal data. "
        "Each plan item must be a safe visible action, not a purchase, print order, "
        "private-data request, or destructive act."
    )


def _local_agent_traces(object_card: ObjectCard, myth_seed: MythSeed) -> list[NPCAgentTrace]:
    return [
        NPCAgentTrace(
            npc_id="mara",
            name="Mara",
            belief=f"{object_card.label} is a sign that the village has been heard.",
            intention="welcome the relic into public witness",
            proposed_action="approach_artifact",
            rationale="Mara interprets awe as a safe invitation to gather and witness.",
            confidence=0.84,
        ),
        NPCAgentTrace(
            npc_id="ior",
            name="Ior",
            belief=f"{myth_seed.title} may be a test rather than a gift.",
            intention="protect the village until the relic proves safe",
            proposed_action="keep_distance",
            rationale="Ior starts with caution because unverified artifacts can shift village trust.",
            confidence=0.72,
        ),
        NPCAgentTrace(
            npc_id="senn",
            name="Senn",
            belief="The artifact should be named before anyone tries to use it.",
            intention="turn curiosity into a shared ritual language",
            proposed_action="suggest_ritual_name",
            rationale="Senn believes naming a strange object makes it easier to debate safely.",
            confidence=0.78,
        ),
    ]


def _local_reactions_from_traces(
    agent_traces: list[NPCAgentTrace],
    myth_seed: MythSeed,
) -> list[NPCReaction]:
    trace_by_id = {trace.npc_id: trace for trace in agent_traces}
    return [
        NPCReaction(
            npc_id="mara",
            name="Mara",
            emotion="awe",
            interpretation=trace_by_id["mara"].belief,
            plan=[
                trace_by_id["mara"].proposed_action,
                "kneel_near_artifact",
                "invite_neighbors_to_witness",
            ],
            world_change="faith_in_player_increases",
        ),
        NPCReaction(
            npc_id="ior",
            name="Ior",
            emotion="suspicion",
            interpretation=trace_by_id["ior"].belief,
            plan=[
                trace_by_id["ior"].proposed_action,
                "question_mara",
                "propose_guarding_the_artifact_overnight",
            ],
            world_change="village_debate_starts",
        ),
        NPCReaction(
            npc_id="senn",
            name="Senn",
            emotion="curiosity",
            interpretation=trace_by_id["senn"].belief,
            plan=[
                "circle_artifact",
                "sketch_symbol_in_dirt",
                trace_by_id["senn"].proposed_action,
            ],
            world_change="artifact_gets_a_local_name",
        ),
    ]


def _validated_agent_traces(
    agent_traces: list[NPCAgentTrace],
    reactions: list[NPCReaction],
) -> list[NPCAgentTrace]:
    if not agent_traces:
        return _agent_traces_from_reactions(reactions)

    fallback_by_id = {
        trace.npc_id: trace
        for trace in _agent_traces_from_reactions(reactions)
    }
    reactions_by_id = {reaction.npc_id: reaction for reaction in reactions}
    validated: list[NPCAgentTrace] = []
    for trace in agent_traces:
        reaction = reactions_by_id.get(trace.npc_id)
        if not reaction:
            validated.append(trace)
            continue
        planned_actions = {_normalized_action(action) for action in reaction.plan}
        if _normalized_action(trace.proposed_action) not in planned_actions:
            validated.append(fallback_by_id[trace.npc_id])
            continue
        validated.append(trace)
    return validated


def _agent_traces_from_reactions(reactions: list[NPCReaction]) -> list[NPCAgentTrace]:
    return [
        NPCAgentTrace(
            npc_id=reaction.npc_id,
            name=reaction.name,
            belief=reaction.interpretation,
            intention=reaction.world_change.replace("_", " "),
            proposed_action=reaction.plan[0] if reaction.plan else "observe_artifact",
            rationale="Synthesized from a structured NPC reaction that did not include an explicit agent trace.",
            confidence=0.5,
        )
        for reaction in reactions
    ]


def _normalized_action(action: str) -> str:
    return action.strip().lower()


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
