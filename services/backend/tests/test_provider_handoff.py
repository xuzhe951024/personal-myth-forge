from myth_forge_api.config import Settings
from myth_forge_api.provider_handoff import build_provider_handoff_report


def test_provider_handoff_blocks_default_local_core_provider_with_next_action() -> None:
    report = build_provider_handoff_report(Settings())

    assert report["status"] == "blocked"
    assert report["first_blocker"]["id"] == "three_d_provider"
    assert report["first_blocker"]["classification"] == "local_stub"
    assert "THREE_D_PROVIDER=meshy" in report["first_blocker"]["command"]
    assert report["first_blocker"]["validation_command"] == "make provider-handoff"
    assert report["next_action"] == {
        **report["first_blocker"],
        "source": "first_blocker",
    }
    assert "make provider-handoff" in report["operator_actions"]
    assert report["safety"]["provider_calls"] is False
    assert report["safety"]["provider_secrets_in_report"] is False


def test_provider_handoff_prefers_missing_env_for_selected_real_provider() -> None:
    report = build_provider_handoff_report(
        Settings(three_d_provider="meshy", npc_provider="openai")
    )

    assert report["status"] == "blocked"
    assert report["missing_env"] == ["MESHY_API_KEY", "OPENAI_API_KEY"]
    assert report["first_blocker"]["id"] == "MESHY_API_KEY"
    assert report["first_blocker"]["classification"] == "missing_required_env"
    assert report["first_blocker"]["command"] == (
        "provide MESHY_API_KEY in final-resources.env"
    )
    assert report["first_blocker"]["validation_command"] == (
        "make final-resources-preflight"
    )
    assert report["next_action"]["source"] == "first_blocker"


def test_provider_handoff_ready_has_no_blocker_or_next_action() -> None:
    report = build_provider_handoff_report(
        Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        )
    )

    assert report["status"] == "ready"
    assert report["core_real_ready"] is True
    assert report["first_blocker"] is None
    assert report["next_action"] is None
    assert report["operator_actions"] == []
