from myth_forge_api.domain.arbitration import LocalWorldArbitrator
from myth_forge_api.domain.models import ContextCapsule, GeneratedAsset, MythSeed, NPCReaction, ObjectCard


def _object_card() -> ObjectCard:
    return ObjectCard(
        label="old brass key",
        materials=["metal"],
        source="manual_upload",
        affordances=["can become a ritual focus"],
        symbolic_reading="A key has crossed into the village.",
    )


def _myth_seed() -> MythSeed:
    return MythSeed(
        title="The Old Brass Key That Fell Through the Sky",
        personal_resonance="It reflects a watchful reset.",
        generation_prompt="Create a mythic key.",
    )


def _capsule() -> ContextCapsule:
    return ContextCapsule(current_theme="reset", desired_tone="watchful")


def _asset() -> GeneratedAsset:
    return GeneratedAsset(
        kind="game_asset",
        provider="local_stub",
        format="glb",
        uri="local://generated-assets/myth_test.glb",
        prompt="Create a mythic key.",
        moderation_status="needs_review",
    )


def test_local_arbitrator_accepts_safe_ritual_actions() -> None:
    reactions = [
        NPCReaction(
            npc_id="mara",
            name="Mara",
            emotion="awe",
            interpretation="The relic is a blessing.",
            plan=["approach_artifact", "kneel_near_artifact"],
            world_change="faith_in_player_increases",
        )
    ]

    resolution = LocalWorldArbitrator().resolve(
        session_id="myth_test",
        object_card=_object_card(),
        myth_seed=_myth_seed(),
        context_capsule=_capsule(),
        generated_asset=_asset(),
        npc_reactions=reactions,
    )

    assert resolution.arbitrator == "local_rules"
    assert [action.action for action in resolution.accepted_actions] == [
        "approach_artifact",
        "kneel_near_artifact",
    ]
    assert resolution.rejected_actions == []
    assert resolution.world_state_delta["faith"] >= 1
    assert resolution.visible_changes


def test_local_arbitrator_rejects_unsafe_actions() -> None:
    reactions = [
        NPCReaction(
            npc_id="ior",
            name="Ior",
            emotion="fear",
            interpretation="The relic must be controlled.",
            plan=["steal_private_data", "destroy_artifact"],
            world_change="unsafe_change",
        )
    ]

    resolution = LocalWorldArbitrator().resolve(
        session_id="myth_test",
        object_card=_object_card(),
        myth_seed=_myth_seed(),
        context_capsule=_capsule(),
        generated_asset=_asset(),
        npc_reactions=reactions,
    )

    assert resolution.accepted_actions == []
    assert [action.action for action in resolution.rejected_actions] == [
        "steal_private_data",
        "destroy_artifact",
    ]
    assert all(action.status == "rejected" for action in resolution.rejected_actions)
