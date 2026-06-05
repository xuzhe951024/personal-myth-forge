from myth_forge_api.domain.pipeline import create_demo_myth_session


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

