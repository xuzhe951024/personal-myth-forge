from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from pydantic import BaseModel, Field

from myth_forge_api.domain.arbitration import LocalWorldArbitrator, WorldArbitrator
from myth_forge_api.domain.models import (
    ContextCapsule,
    NPCAgentTick,
    NPCAgentTickRequest,
    NPCAgentTrace,
    NPCReaction,
)
from myth_forge_api.providers.npc import (
    EXPECTED_NPC_ID_LIST,
    EXPECTED_NPC_IDS,
    OpenAINPCConfigurationError,
    OpenAINPCProviderError,
    _sanitize_provider_error,
    _validated_agent_traces,
)

if TYPE_CHECKING:
    from myth_forge_api.config import Settings


class NPCTickRuntime(Protocol):
    runtime_name: str

    def generate_tick(self, request: NPCAgentTickRequest) -> NPCAgentTick:
        ...


class LocalNPCTickRuntime:
    runtime_name = "local_tick_runtime"

    def __init__(self, world_arbitrator: WorldArbitrator | None = None) -> None:
        self.world_arbitrator = world_arbitrator or LocalWorldArbitrator()

    def generate_tick(self, request: NPCAgentTickRequest) -> NPCAgentTick:
        session = request.session
        event_summary = _recent_event_summary(request.recent_events)
        traces = _tick_traces(request, event_summary)
        reactions = _reactions_from_traces(traces)
        world_resolution = self.world_arbitrator.resolve(
            session_id=session.session_id,
            object_card=session.object_card,
            myth_seed=session.myth_seed,
            context_capsule=_tick_context_capsule(request),
            generated_asset=session.generated_asset,
            npc_reactions=reactions,
        )
        return NPCAgentTick(
            session_id=session.session_id,
            tick_index=request.tick_index,
            agent_runtime=self.runtime_name,
            npc_agent_traces=traces,
            npc_reactions=reactions,
            world_resolution=world_resolution,
        )


class OpenAINPCTickOutput(BaseModel):
    reactions: list[NPCReaction]
    agent_traces: list[NPCAgentTrace] = Field(default_factory=list)


class OpenAINPCTickRuntime:
    runtime_name = "openai_tick_structured_runtime"

    def __init__(
        self,
        api_key: str | None,
        model: str,
        api_base_url: str | None = None,
        client: Any | None = None,
        world_arbitrator: WorldArbitrator | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.api_base_url = api_base_url
        self.client = client
        self.world_arbitrator = world_arbitrator or LocalWorldArbitrator()

    @classmethod
    def from_settings(cls, settings: Settings) -> OpenAINPCTickRuntime:
        return cls(
            api_key=settings.openai_api_key,
            model=settings.openai_npc_model,
            api_base_url=settings.openai_api_base_url,
        )

    def validate_configuration(self) -> None:
        if not self.api_key:
            raise OpenAINPCConfigurationError("OPENAI_API_KEY is required for NPC tick generation.")

    def generate_tick(self, request: NPCAgentTickRequest) -> NPCAgentTick:
        self.validate_configuration()
        client = self.client or self._build_client()
        try:
            response = client.responses.parse(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You advance three text-only NPC agents for Personal Myth Forge. "
                            "Use only the approved myth session summary. Raw private data, "
                            "messages, calendar text, provider keys, and media payloads are "
                            "not available."
                        ),
                    },
                    {
                        "role": "user",
                        "content": _openai_tick_prompt(request),
                    },
                ],
                text_format=OpenAINPCTickOutput,
            )
            output = OpenAINPCTickOutput.model_validate(response.output_parsed)
        except OpenAINPCProviderError:
            raise
        except Exception as exc:
            message = _sanitize_provider_error(exc, secret=self.api_key)
            raise OpenAINPCProviderError(f"OpenAI NPC tick generation failed: {message}") from exc

        npc_ids = {reaction.npc_id for reaction in output.reactions}
        if len(output.reactions) != 3 or npc_ids != EXPECTED_NPC_IDS:
            expected = ", ".join(EXPECTED_NPC_ID_LIST)
            raise OpenAINPCProviderError(
                f"OpenAI NPC tick response must include exactly: {expected}."
            )

        agent_traces = _validated_agent_traces(output.agent_traces, output.reactions)
        trace_ids = {trace.npc_id for trace in agent_traces}
        if len(agent_traces) != 3 or trace_ids != EXPECTED_NPC_IDS:
            expected = ", ".join(EXPECTED_NPC_ID_LIST)
            raise OpenAINPCProviderError(
                f"OpenAI NPC tick traces must include exactly: {expected}."
            )

        session = request.session
        world_resolution = self.world_arbitrator.resolve(
            session_id=session.session_id,
            object_card=session.object_card,
            myth_seed=session.myth_seed,
            context_capsule=_tick_context_capsule(request),
            generated_asset=session.generated_asset,
            npc_reactions=output.reactions,
        )
        return NPCAgentTick(
            session_id=session.session_id,
            tick_index=request.tick_index,
            agent_runtime=self.runtime_name,
            npc_agent_traces=agent_traces,
            npc_reactions=output.reactions,
            world_resolution=world_resolution,
        )

    def _build_client(self) -> Any:
        from openai import OpenAI

        kwargs: dict[str, str] = {"api_key": self.api_key or ""}
        if self.api_base_url:
            kwargs["base_url"] = self.api_base_url
        return OpenAI(**kwargs)


def _openai_tick_prompt(request: NPCAgentTickRequest) -> str:
    session = request.session
    return (
        f"Session: {session.session_id}\n"
        f"Tick index: {request.tick_index}\n"
        f"Object label: {session.object_card.label}\n"
        f"Materials: {', '.join(session.object_card.materials) or 'unknown'}\n"
        f"Symbolic reading: {session.object_card.symbolic_reading}\n"
        f"Myth title: {session.myth_seed.title}\n"
        f"Personal resonance summary: {session.myth_seed.personal_resonance}\n"
        f"Asset provider: {session.generated_asset.provider}\n"
        f"Asset format: {session.generated_asset.format}\n"
        f"Recent village event summary: {_recent_event_summary(request.recent_events)}\n"
        "Return exactly three reactions for NPC ids mara, ior, and senn. "
        "Also return one agent trace per NPC with belief, intention, proposed_action, "
        "rationale, and confidence. Each proposed_action must also appear in that NPC's plan. "
        "Each plan item must be a safe visible action, not a purchase, print order, "
        "private-data request, media payload request, or destructive act."
    )


def _tick_traces(
    request: NPCAgentTickRequest,
    event_summary: str,
) -> list[NPCAgentTrace]:
    session = request.session
    label = session.object_card.label
    tick = request.tick_index
    return [
        NPCAgentTrace(
            npc_id="mara",
            name="Mara",
            belief=f"After sign {tick}, {label} is becoming a public promise.",
            intention="turn first awe into shared witness",
            proposed_action="invite_neighbors_to_witness",
            rationale=f"Mara updates her plan from the prior village response and {event_summary}.",
            confidence=0.82,
        ),
        NPCAgentTrace(
            npc_id="ior",
            name="Ior",
            belief=f"The village still needs rules before anyone handles {label}.",
            intention="keep the artifact guarded without stopping debate",
            proposed_action="guard_artifact",
            rationale=f"Ior weighs the accepted actions against {event_summary}.",
            confidence=0.74,
        ),
        NPCAgentTrace(
            npc_id="senn",
            name="Senn",
            belief=f"{session.myth_seed.title} needs a phrase everyone can repeat.",
            intention="make the relic legible through ritual language",
            proposed_action="suggest_ritual_name",
            rationale=f"Senn turns the latest village mood and {event_summary} into a safer name.",
            confidence=0.79,
        ),
    ]


def _reactions_from_traces(traces: list[NPCAgentTrace]) -> list[NPCReaction]:
    reactions: list[NPCReaction] = []
    for trace in traces:
        reactions.append(
            NPCReaction(
                npc_id=trace.npc_id,
                name=trace.name,
                emotion=_emotion_for_trace(trace.npc_id),
                interpretation=trace.belief,
                plan=[trace.proposed_action],
                world_change=_world_change_for_trace(trace.npc_id),
            )
        )
    return reactions


def _emotion_for_trace(npc_id: str) -> str:
    return {
        "mara": "awe",
        "ior": "suspicion",
        "senn": "curiosity",
    }.get(npc_id, "focus")


def _world_change_for_trace(npc_id: str) -> str:
    return {
        "mara": "faith_in_player_increases",
        "ior": "village_debate_starts",
        "senn": "artifact_gets_a_local_name",
    }.get(npc_id, "village_attention_shifts")


def _recent_event_summary(recent_events: list[str]) -> str:
    count = len([event for event in recent_events if event.strip()])
    if count == 1:
        return "1 recent village event"
    return f"{count} recent village events"


def _tick_context_capsule(request: NPCAgentTickRequest) -> ContextCapsule:
    return ContextCapsule(
        current_theme=f"agent tick {request.tick_index}",
        desired_tone="autonomous, readable, safe",
        recent_milestone=request.session.myth_seed.title,
    )
