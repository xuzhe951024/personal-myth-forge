from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Any, Mapping

from myth_forge_api.domain.arbitration import LocalWorldArbitrator, WorldArbitrator
from myth_forge_api.domain.models import (
    ContextCapsule,
    MythSeed,
    MythSession,
    ObjectCard,
    ObjectObservation,
)
from myth_forge_api.providers.npc import LocalNPCDirector, NPCDirector
from myth_forge_api.providers.printing import LocalPrintProvider
from myth_forge_api.providers.printing import PrintProvider
from myth_forge_api.providers.three_d import (
    LocalThreeDProvider,
    ThreeDGenerationRequest,
    ThreeDProvider,
    ThreeDSourceAsset,
    ThreeDSourceImage,
)


def create_demo_myth_session(
    object_observation: ObjectObservation | Mapping[str, Any],
    context_capsule: ContextCapsule | Mapping[str, Any],
    three_d_provider: ThreeDProvider | None = None,
    print_provider: PrintProvider | None = None,
    npc_director: NPCDirector | None = None,
    world_arbitrator: WorldArbitrator | None = None,
    source_images: Sequence[ThreeDSourceImage] = (),
    source_assets: Sequence[ThreeDSourceAsset] = (),
) -> MythSession:
    observation = _coerce_object_observation(object_observation)
    capsule = _coerce_context_capsule(context_capsule)
    session_id = _stable_session_id(observation, capsule)

    object_card = _create_object_card(observation)
    myth_seed = _create_myth_seed(object_card, capsule)
    selected_three_d_provider = three_d_provider or LocalThreeDProvider()
    selected_npc_director = npc_director or LocalNPCDirector()
    selected_npc_director.validate_configuration()
    generated_asset = selected_three_d_provider.generate_game_asset(
        ThreeDGenerationRequest(
            session_id=session_id,
            prompt=myth_seed.generation_prompt,
            source_images=tuple(source_images),
            source_assets=tuple(source_assets),
        )
    )
    npc_result = selected_npc_director.generate_reactions(
        session_id=session_id,
        object_card=object_card,
        myth_seed=myth_seed,
        context_capsule=capsule,
        generated_asset=generated_asset,
    )
    npc_reactions = npc_result.reactions
    selected_world_arbitrator = world_arbitrator or LocalWorldArbitrator()
    world_resolution = selected_world_arbitrator.resolve(
        session_id=session_id,
        object_card=object_card,
        myth_seed=myth_seed,
        context_capsule=capsule,
        generated_asset=generated_asset,
        npc_reactions=npc_reactions,
    )
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

    capture_id = getattr(observation, "capture_id", None)
    media_refs = getattr(observation, "media_refs", None)
    if capture_id:
        affordances.append("uploaded capture media")

    symbolic_reading = (
        f"A real-world {observation.label} made of {material_phrase} has crossed into the "
        "village as evidence of a private omen."
    )
    if capture_id:
        media_count = len(media_refs) if isinstance(media_refs, list) else 0
        media_ref_text = ", ".join(media_refs) if isinstance(media_refs, list) else ""
        symbolic_reading += (
            f" Capture evidence: capture_id: {capture_id}; media_refs: {media_count}; "
            f"media_ref_uris: {media_ref_text}."
        )

    return ObjectCard(
        label=observation.label,
        materials=observation.materials,
        source=observation.source,
        affordances=affordances,
        symbolic_reading=symbolic_reading,
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
