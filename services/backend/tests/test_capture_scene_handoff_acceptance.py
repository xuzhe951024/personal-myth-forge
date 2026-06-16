import json

from myth_forge_api.capture_scene_handoff_acceptance import (
    run_capture_scene_handoff_acceptance,
)


def test_capture_scene_handoff_acceptance_runs_guided_scan_to_scene_asset() -> None:
    result = run_capture_scene_handoff_acceptance()

    report_text = json.dumps(result.report)
    assert result.exit_code == 0
    assert result.report["kind"] == "capture_scene_handoff_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 8, "failed": 0}
    assert result.report["capture"] == {
        "capture_mode": "guided_scan",
        "media_count": 2,
    }
    assert result.report["generation_provenance"]["input_mode"] == "multi_image"
    assert result.report["generation_provenance"]["source_image_count"] == 2
    assert result.report["generation_provenance"]["selected_source_image_count"] == 2
    assert result.report["game_asset"]["uri"].startswith(
        "http://testserver/v1/generated-assets/"
    )
    assert result.report["game_asset"]["uri"].endswith("/game.glb")
    assert result.report["scene_asset"]["format"] == "dae"
    assert result.report["scene_asset"]["uri"].startswith(
        "http://testserver/v1/generated-assets/"
    )
    assert result.report["scene_asset"]["uri"].endswith("/scene.dae")
    assert result.report["safety"] == {
        "provider_calls": False,
        "temporary_app_patch_restored": True,
        "raw_media_in_report": False,
        "local_capture_uris_in_report": False,
        "local_paths_in_report": False,
        "provider_secrets_in_report": False,
    }
    assert "data:image" not in report_text
    assert "local-capture://" not in report_text
    assert "/tmp" not in report_text
    assert "/Users/" not in report_text
    assert "Authorization" not in report_text
    assert "Bearer " not in report_text


def test_capture_scene_handoff_ignores_configured_provider_env(monkeypatch) -> None:
    monkeypatch.setenv("THREE_D_PROVIDER", "meshy")
    monkeypatch.setenv("NPC_PROVIDER", "openai")
    monkeypatch.delenv("MESHY_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = run_capture_scene_handoff_acceptance()

    assert result.exit_code == 0
    assert result.report["game_asset"]["uri"].startswith(
        "http://testserver/v1/generated-assets/"
    )
