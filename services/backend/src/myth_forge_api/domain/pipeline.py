from __future__ import annotations

import hashlib
import json
from typing import Mapping, Any

from myth_forge_api.domain.models import (
    ContextCapsule,
    MythSeed,
    MythSession,
    NPCReaction,
    ObjectCard,
    ObjectObservation,
    ResolvedNPCAction,
    WorldResolution,
)
from myth_forge_api.providers.printing import LocalPrintProvider
from myth_forge_api.providers.printing import PrintProvider
from myth_forge_api.providers.npc import LocalNPCDirector, NPCDirector
from myth_forge_api.providers.three_d import LocalThreeDProvider, ThreeDProvider


def create_demo_myth_session(
    object_observation: ObjectObservation | Mapping[str, Any],
    context_capsule: ContextCapsule | Mapping[str, Any],
    three_d_provider: ThreeDProvider | None = None,
    print_provider: PrintProvider | None = None,
    npc_director: NPCDirector | None = None,
) -> MythSession:
    observation = _coerce_object_observation(object_observation)
    capsule = _coerce_context_capsule(context_capsule)
    session_id = _stable_session_id(observation, capsule)

    object_card = _create_object_card(observation)
    myth_seed = _create_myth_seed(object_card, capsule)
    selected_three_d_provider = three_d_provider or LocalThreeDProvider()
    generated_asset = selected_three_d_provider.generate_game_asset(
        session_id=session_id,
        prompt=myth_seed.generation_prompt,
    )
    selected_npc_director = npc_director or LocalNPCDirector()
    npc_result = selected_npc_director.generate_reactions(
        session_id=session_id,
        object_card=object_card,
        myth_seed=myth_seed,
        context_capsule=capsule,
        generated_asset=generated_asset,
    )
    npc_reactions = npc_result.reactions
    world_resolution = _create_world_resolution(npc_reactions)
    selected_print_provider = print_provider or LocalPrintProvider()
    print_candidate = selected_print_provider.create_print_candidate(generated_asset)

    return MythSession(
        session_id=session_id,
        status="ready_for_review",
        object_card=object_card,
        myth_seed=myth_seed,
        generated_asset=generated_asset,
        npc_director=npc_result.provider,
        npc_reactions=npc_reactions,
        world_resolution=world_resolution,
        print_candidate=print_candidate,
    )


def _coerce_object_observation(
    object_observation: ObjectObservation | Mapping[str, Any],
) -> ObjectObservation:
    if isinstance(object_observation, ObjectObservation):
        return object_observation
    return ObjectObservation.model_validate(object_observation)


def _coerce_context_capsule(context_capsule: ContextCapsule | Mapping[str, Any]) -> ContextCapsule:
    if isinstance(context_capsule, ContextCapsule):
        return context_capsule
    return ContextCapsule.model_validate(context_capsule)


def _stable_session_id(observation: ObjectObservation, capsule: ContextCapsule) -> str:
    payload = {
        "object": observation.model_dump(mode="json"),
        "context": capsule.model_dump(mode="json"),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return f"myth_{digest[:16]}"


def _create_object_card(observation: ObjectObservation) -> ObjectCard:
    material_phrase = ", ".join(observation.materials) if observation.materials else "unknown matter"
    affordances = [
        f"can be approached as a {observation.label}",
        "can become a ritual focus",
        "can alter local belief when witnessed by NPCs",
    ]

    if "metal" in {material.lower() for material in observation.materials}:
        affordances.append("can symbolize endurance, locks, oaths, or hidden passages")

    return ObjectCard(
        label=observation.label,
        materials=observation.materials,
        source=observation.source,
        affordances=affordances,
        symbolic_reading=(
            f"A real-world {observation.label} made of {material_phrase} has crossed into the "
            "village as evidence of a private omen."
        ),
    )


def _create_myth_seed(object_card: ObjectCard, capsule: ContextCapsule) -> MythSeed:
    title = f"The {object_card.label.title()} That Fell Through the Sky"
    resonance = (
        f"The artifact refracts the player's current theme of {capsule.current_theme}"
        f" with a {capsule.desired_tone} tone."
    )
    if capsule.recent_milestone:
        resonance += f" It quietly echoes the milestone: {capsule.recent_milestone}."

    return MythSeed(
        title=title,
        personal_resonance=resonance,
        generation_prompt=(
            "Create a free-form mythic 3D artifact inspired by "
            f"{object_card.label}. Preserve the object's recognizable silhouette, but transform "
            f"it into a strange village relic. Emotional tone: {capsule.desired_tone}. "
            "The result must be game-ready as a GLB and suitable for later print adaptation."
        ),
    )


def _create_world_resolution(npc_reactions: list[NPCReaction]) -> WorldResolution:
    accepted_actions = [
        ResolvedNPCAction(
            npc_id=reaction.npc_id,
            action=reaction.plan[0],
            status="accepted",
            reason="safe ritual action",
        )
        for reaction in npc_reactions
        if reaction.plan
    ]

    return WorldResolution(
        arbitrator="local_rules",
        summary="The village begins interpreting the relic.",
        accepted_actions=accepted_actions,
        rejected_actions=[],
        world_state_delta={
            "faith": 1,
            "curiosity": 1,
            "suspicion": 1,
            "debate_intensity": 1,
            "artifact_renown": 1,
        },
        visible_changes=[
            "The artifact gains a local name.",
            "The village debate begins.",
        ],
    )
