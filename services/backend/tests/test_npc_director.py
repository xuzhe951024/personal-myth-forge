from myth_forge_api.domain.models import ContextCapsule, GeneratedAsset, MythSeed, ObjectCard
from myth_forge_api.providers.npc import LocalNPCDirector


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


def test_local_npc_director_returns_stable_three_npc_reactions() -> None:
    result = LocalNPCDirector().generate_reactions(
        session_id="myth_test",
        object_card=_object_card(),
        myth_seed=_myth_seed(),
        context_capsule=_capsule(),
        generated_asset=_asset(),
    )

    assert result.provider == "local_stub"
    assert {reaction.npc_id for reaction in result.reactions} == {"mara", "ior", "senn"}
    assert all(reaction.plan for reaction in result.reactions)
