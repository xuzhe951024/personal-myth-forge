from __future__ import annotations

from typing import Protocol

from myth_forge_api.domain.arbitration import LocalWorldArbitrator, WorldArbitrator
from myth_forge_api.domain.models import (
    ContextCapsule,
    NPCAgentTick,
    NPCAgentTickRequest,
    NPCAgentTrace,
    NPCReaction,
)


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
