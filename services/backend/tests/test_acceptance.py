import json

from myth_forge_api.acceptance import run_demo_acceptance
from myth_forge_api.config import Settings
from myth_forge_api.providers.npc import LocalNPCDirector
from myth_forge_api.providers.npc_ticks import LocalNPCTickRuntime
from myth_forge_api.providers.three_d import MeshyProviderError
from myth_forge_api.providers.three_d import LocalThreeDProvider


def test_demo_acceptance_local_report_runs_bounded_ticks(tmp_path) -> None:
    result = run_demo_acceptance(
        settings=Settings(myth_session_storage_dir=str(tmp_path / "sessions")),
        provider_mode="local",
        npc_steps=3,
        require_real_core=False,
    )

    report_text = json.dumps(result.report)
    assert result.exit_code == 0
    assert result.report["kind"] == "demo_acceptance_report"
    assert result.report["mode"] == "local"
    assert result.report["status"] == "succeeded"
    assert result.report["session"]["session_id"].startswith("myth_")
    assert result.report["session"]["generated_asset_provider"] == "local_stub"
    assert result.report["session"]["generated_asset_format"] == "glb"
    assert result.report["session"]["generation_provenance"]["input_mode"] == "text_prompt"
    assert result.report["session"]["generation_provenance"]["provider_route"] == "local_stub"
    assert result.report["session"]["generation_provenance"]["raw_sources_included"] is False
    assert result.report["session"]["scene_variant_uri"].endswith(".dae")
    assert result.report["session"]["print_candidate_format"] == "3mf"
    assert result.report["npc"]["initial_runtime"] == "local_agent_runtime"
    assert result.report["npc"]["requested_steps"] == 3
    assert result.report["npc"]["completed_steps"] == 3
    assert result.report["npc"]["latest_tick_index"] == 3
    assert result.report["npc"]["tick_runtime"] == "local_tick_runtime"
    assert result.report["safety"]["raw_media_in_report"] is False
    assert result.report["safety"]["raw_personal_source_in_report"] is False
    assert "MESHY_API_KEY" not in report_text
    assert "OPENAI_API_KEY" not in report_text
    assert "data:image" not in report_text
    assert str(tmp_path) not in report_text


def test_demo_acceptance_zero_steps_skips_tick_generation(tmp_path) -> None:
    result = run_demo_acceptance(
        settings=Settings(myth_session_storage_dir=str(tmp_path / "sessions")),
        provider_mode="local",
        npc_steps=0,
        require_real_core=False,
    )

    assert result.exit_code == 0
    assert result.report["status"] == "succeeded"
    assert result.report["npc"]["requested_steps"] == 0
    assert result.report["npc"]["completed_steps"] == 0
    assert result.report["npc"]["latest_tick_index"] is None
    assert result.report["npc"]["tick_runtime"] is None


def test_demo_acceptance_strict_configured_mode_exits_two_before_provider_calls(
    tmp_path,
    monkeypatch,
) -> None:
    def fail_if_called(settings):
        raise AssertionError("provider should not be built before readiness passes")

    monkeypatch.setattr("myth_forge_api.acceptance.build_three_d_provider", fail_if_called)
    monkeypatch.setattr("myth_forge_api.acceptance.build_npc_director", fail_if_called)
    monkeypatch.setattr("myth_forge_api.acceptance.build_npc_tick_runtime", fail_if_called)
    result = run_demo_acceptance(
        settings=Settings(
            three_d_provider="meshy",
            npc_provider="openai",
            myth_session_storage_dir=str(tmp_path / "sessions"),
        ),
        provider_mode="configured",
        npc_steps=3,
        require_real_core=True,
    )

    assert result.exit_code == 2
    assert result.report["status"] == "not_ready"
    assert result.report["core_real_ready"] is False
    assert result.report["missing_env"] == ["MESHY_API_KEY", "OPENAI_API_KEY"]
    assert result.report["error"] == "Core providers are not real-provider-ready."


def test_demo_acceptance_configured_requires_live_provider_consent_before_calls(
    tmp_path,
    monkeypatch,
) -> None:
    def fail_if_called(settings):
        raise AssertionError("live providers should not be built without consent")

    monkeypatch.setattr("myth_forge_api.acceptance.build_three_d_provider", fail_if_called)
    monkeypatch.setattr("myth_forge_api.acceptance.build_npc_director", fail_if_called)
    monkeypatch.setattr("myth_forge_api.acceptance.build_npc_tick_runtime", fail_if_called)

    result = run_demo_acceptance(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-secret",
            npc_provider="openai",
            openai_api_key="sk-openai-secret",
            myth_session_storage_dir=str(tmp_path / "sessions"),
        ),
        provider_mode="configured",
        npc_steps=3,
        require_real_core=True,
    )

    report_text = json.dumps(result.report)
    assert result.exit_code == 2
    assert result.report["status"] == "not_ready"
    assert result.report["core_real_ready"] is True
    assert result.report["allow_live_provider_calls"] is False
    assert result.report["live_provider_consent_required"] is True
    assert result.report["live_provider_kinds"] == ["three_d", "npc"]
    assert result.report["selected_providers"] == {
        "three_d": "meshy",
        "npc": "openai",
        "capture_storage": "local_filesystem",
    }
    assert result.report["missing_env"] == []
    assert result.report["error"] == (
        "Live provider calls require --allow-live-provider-calls."
    )
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text


def test_demo_acceptance_configured_allows_live_provider_calls_when_explicit(
    tmp_path,
    monkeypatch,
) -> None:
    builder_calls: list[str] = []

    def fake_three_d_provider(settings):
        builder_calls.append(f"three_d:{settings.three_d_provider}")
        return LocalThreeDProvider()

    def fake_npc_director(settings):
        builder_calls.append(f"npc:{settings.npc_provider}")
        return LocalNPCDirector()

    def fake_tick_runtime(settings):
        builder_calls.append(f"tick:{settings.npc_provider}")
        return LocalNPCTickRuntime()

    monkeypatch.setattr("myth_forge_api.acceptance.build_three_d_provider", fake_three_d_provider)
    monkeypatch.setattr("myth_forge_api.acceptance.build_npc_director", fake_npc_director)
    monkeypatch.setattr("myth_forge_api.acceptance.build_npc_tick_runtime", fake_tick_runtime)

    result = run_demo_acceptance(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-secret",
            npc_provider="openai",
            openai_api_key="sk-openai-secret",
            myth_session_storage_dir=str(tmp_path / "sessions"),
        ),
        provider_mode="configured",
        npc_steps=1,
        require_real_core=True,
        allow_live_provider_calls=True,
    )

    assert result.exit_code == 0
    assert result.report["status"] == "succeeded"
    assert result.report["allow_live_provider_calls"] is True
    assert result.report["live_provider_consent_required"] is False
    assert result.report["live_provider_kinds"] == ["three_d", "npc"]
    assert builder_calls == ["three_d:meshy", "npc:openai", "tick:openai"]


class FailingThreeDProvider:
    provider_name = "failing_three_d"

    def generate_game_asset(self, request):
        raise MeshyProviderError("failed Authorization=Bearer test-secret raw=private")


def test_demo_acceptance_provider_failure_is_sanitized(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "myth_forge_api.acceptance.build_three_d_provider",
        lambda settings: FailingThreeDProvider(),
    )

    result = run_demo_acceptance(
        settings=Settings(myth_session_storage_dir=str(tmp_path / "sessions")),
        provider_mode="configured",
        npc_steps=3,
        require_real_core=False,
    )

    report_text = json.dumps(result.report)
    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["error"]
    assert "test-secret" not in report_text
    assert "Authorization" not in report_text
    assert "raw=private" not in report_text
