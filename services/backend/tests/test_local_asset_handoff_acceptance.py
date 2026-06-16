import json

from myth_forge_api.local_asset_handoff_acceptance import (
    run_local_asset_handoff_acceptance,
)


def test_local_asset_handoff_acceptance_downloads_safe_scene_asset() -> None:
    result = run_local_asset_handoff_acceptance()

    report_text = json.dumps(result.report)
    assert result.exit_code == 0
    assert result.report["kind"] == "local_asset_handoff_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 6, "failed": 0}
    assert result.report["generated_asset_provider"] == "local_stub"
    assert result.report["game_asset"]["uri"].startswith(
        "http://testserver/v1/generated-assets/"
    )
    assert result.report["game_asset"]["uri"].endswith("/game.glb")
    assert result.report["scene_variant"]["format"] == "dae"
    assert result.report["scene_variant"]["uri"].startswith(
        "http://testserver/v1/generated-assets/"
    )
    assert result.report["scene_variant"]["uri"].endswith("/scene.dae")
    assert result.report["scene_variant"]["is_scene_loadable"] is True
    assert result.report["safety"] == {
        "provider_calls": False,
        "global_mutation": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "local_paths_in_report": False,
    }
    assert "local://" not in report_text
    assert "data:image" not in report_text
    assert "/tmp" not in report_text


def test_local_asset_handoff_ignores_configured_provider_env(monkeypatch) -> None:
    monkeypatch.setenv("THREE_D_PROVIDER", "meshy")
    monkeypatch.setenv("NPC_PROVIDER", "openai")
    monkeypatch.delenv("MESHY_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = run_local_asset_handoff_acceptance()

    assert result.exit_code == 0
    assert result.report["generated_asset_provider"] == "local_stub"
