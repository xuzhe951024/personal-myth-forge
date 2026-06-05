import pytest

from myth_forge_api.domain.models import (
    GeneratedAsset,
    NPCDirectorResult,
    NPCReaction,
    WorldResolution,
)
from myth_forge_api.domain.pipeline import create_demo_myth_session
from myth_forge_api.providers.npc import OpenAINPCConfigurationError


class RecordingThreeDProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def generate_game_asset(self, session_id: str, prompt: str) -> GeneratedAsset:
        self.calls.append((session_id, prompt))
        return GeneratedAsset(
            kind="game_asset",
            provider="recording",
            format="glb",
            uri=f"recording://{session_id}.glb",
            prompt=prompt,
            moderation_status="needs_review",
        )


class RecordingNPCDirector:
    provider_name = "recording_npc"

    def __init__(self) -> None:
        self.calls: list[str] = []

    def validate_configuration(self) -> None:
        return None

    def generate_reactions(
        self,
        session_id,
        object_card,
        myth_seed,
        context_capsule,
        generated_asset,
    ) -> NPCDirectorResult:
        self.calls.append(session_id)
        return NPCDirectorResult(
            provider=self.provider_name,
            reactions=[
                NPCReaction(
                    npc_id="test",
                    name="Test",
                    emotion="focus",
                    interpretation=f"{object_card.label} is being tested.",
                    plan=["approach_artifact"],
                    world_change="test_change",
                )
            ],
        )


class RecordingWorldArbitrator:
    arbitrator_name = "recording_rules"

    def resolve(
        self,
        session_id,
        object_card,
        myth_seed,
        context_capsule,
        generated_asset,
        npc_reactions,
    ) -> WorldResolution:
        return WorldResolution(
            arbitrator=self.arbitrator_name,
            summary=f"resolved {len(npc_reactions)} reactions for {object_card.label}",
            accepted_actions=[],
            rejected_actions=[],
            world_state_delta={
                "faith": 0,
                "curiosity": 0,
                "suspicion": 0,
                "debate_intensity": 0,
                "artifact_renown": 0,
            },
            visible_changes=["The test arbitrator marked the world quiet."],
        )


class FailingConfigurationNPCDirector:
    provider_name = "failing_npc"

    def validate_configuration(self) -> None:
        raise OpenAINPCConfigurationError("OPENAI_API_KEY is required for NPC generation.")

    def generate_reactions(
        self,
        session_id,
        object_card,
        myth_seed,
        context_capsule,
        generated_asset,
    ) -> NPCDirectorResult:
        raise AssertionError("NPC generation should not run after configuration failure.")


def test_generates_session_from_real_object_and_context() -> None:
    session = create_demo_myth_session(
        object_observation={
            "label": "old brass key",
            "materials": ["metal"],
            "source": "phone_capture",
            "visual_notes": "worn teeth, circular bow, warm reflections",
        },
        context_capsule={
            "current_theme": "deadline pressure",
            "desired_tone": "tender, strange",
            "recent_milestone": "finished a difficult project draft",
        },
    )

    assert session.status == "ready_for_review"
    assert session.object_card.label == "old brass key"
    assert session.object_card.materials == ["metal"]
    assert session.myth_seed.title
    assert "deadline pressure" in session.myth_seed.personal_resonance
    assert {reaction.npc_id for reaction in session.npc_reactions} == {"mara", "ior", "senn"}
    assert all(reaction.plan for reaction in session.npc_reactions)
    assert session.generated_asset.kind == "game_asset"
    assert session.generated_asset.provider == "local_stub"
    assert session.generated_asset.format == "glb"
    assert session.print_candidate.kind == "print_asset"
    assert session.print_candidate.requires_user_approval is True


def test_session_serializes_to_json_safe_payload() -> None:
    session = create_demo_myth_session(
        object_observation={
            "label": "ceramic mug",
            "materials": ["ceramic"],
            "source": "manual_upload",
        },
        context_capsule={
            "current_theme": "quiet reset",
            "desired_tone": "calm and uncanny",
        },
    )

    payload = session.model_dump(mode="json")

    assert payload["object_card"]["label"] == "ceramic mug"
    assert payload["generated_asset"]["uri"].startswith("local://")
    assert payload["print_candidate"]["approval_reason"]


def test_pipeline_accepts_injected_three_d_provider() -> None:
    provider = RecordingThreeDProvider()

    session = create_demo_myth_session(
        object_observation={
            "label": "silver spoon",
            "materials": ["metal"],
            "source": "manual_upload",
        },
        context_capsule={
            "current_theme": "making peace with change",
            "desired_tone": "gentle and uncanny",
        },
        three_d_provider=provider,
    )

    assert session.generated_asset.provider == "recording"
    assert provider.calls == [(session.session_id, session.myth_seed.generation_prompt)]


def test_session_includes_world_resolution_contract() -> None:
    session = create_demo_myth_session(
        object_observation={
            "label": "old brass key",
            "materials": ["metal"],
            "source": "manual_upload",
        },
        context_capsule={
            "current_theme": "choosing a new direction",
            "desired_tone": "watchful and tender",
        },
    )

    payload = session.model_dump(mode="json")

    assert payload["npc_director"] == "local_stub"
    assert payload["world_resolution"]["arbitrator"] == "local_rules"
    assert payload["world_resolution"]["summary"]
    assert isinstance(payload["world_resolution"]["accepted_actions"], list)
    assert isinstance(payload["world_resolution"]["rejected_actions"], list)
    assert "faith" in payload["world_resolution"]["world_state_delta"]
    assert payload["world_resolution"]["visible_changes"]


def test_pipeline_accepts_injected_npc_director() -> None:
    director = RecordingNPCDirector()

    session = create_demo_myth_session(
        object_observation={"label": "coin", "materials": ["metal"], "source": "manual_upload"},
        context_capsule={"current_theme": "choice", "desired_tone": "bright"},
        npc_director=director,
    )

    assert session.npc_director == "recording_npc"
    assert [reaction.npc_id for reaction in session.npc_reactions] == ["test"]
    assert director.calls == [session.session_id]


def test_pipeline_accepts_injected_world_arbitrator() -> None:
    session = create_demo_myth_session(
        object_observation={"label": "coin", "materials": ["metal"], "source": "manual_upload"},
        context_capsule={"current_theme": "choice", "desired_tone": "bright"},
        world_arbitrator=RecordingWorldArbitrator(),
    )

    assert session.world_resolution.arbitrator == "recording_rules"
    assert session.world_resolution.visible_changes == [
        "The test arbitrator marked the world quiet."
    ]


def test_pipeline_validates_npc_director_before_generating_3d() -> None:
    provider = RecordingThreeDProvider()

    with pytest.raises(OpenAINPCConfigurationError):
        create_demo_myth_session(
            object_observation={
                "label": "silver spoon",
                "materials": ["metal"],
                "source": "manual_upload",
            },
            context_capsule={
                "current_theme": "making peace with change",
                "desired_tone": "gentle and uncanny",
            },
            three_d_provider=provider,
            npc_director=FailingConfigurationNPCDirector(),
        )

    assert provider.calls == []


def test_pipeline_includes_capture_reference_in_object_card() -> None:
    session = create_demo_myth_session(
        object_observation={
            "label": "old brass key",
            "materials": ["metal"],
            "source": "phone_capture",
            "capture_id": "cap_test",
            "media_refs": ["local-capture://cap_test/media_0.jpg"],
        },
        context_capsule={"current_theme": "choice", "desired_tone": "bright"},
    )

    assert "cap_test" in session.object_card.symbolic_reading
    assert "uploaded capture media" in session.object_card.affordances
