import json

import pytest

from myth_forge_api.acceptance import DemoAcceptanceResult
from myth_forge_api.config import Settings
from myth_forge_api.cli import main
from myth_forge_api.providers.three_d import MeshyProviderError, ThreeDGenerationRequest


def test_cli_generates_local_asset_json(capsys) -> None:
    exit_code = main(
        ["generate-asset", "--provider", "local", "--prompt", "Create a tiny moon cup."]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider"] == "local_stub"
    assert payload["format"] == "glb"


def test_cli_evaluate_3d_writes_report(tmp_path) -> None:
    prompts_file = tmp_path / "prompts.txt"
    output_file = tmp_path / "report.json"
    prompts_file.write_text("Create a moon cup.\nCreate a brass key.\n", encoding="utf-8")

    exit_code = main(
        [
            "evaluate-3d",
            "--provider",
            "local",
            "--prompts-file",
            str(prompts_file),
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 0
    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert report["provider"] == "local"
    assert report["total_prompts"] == 2
    assert [row["status"] for row in report["rows"]] == ["succeeded", "succeeded"]
    assert all("elapsed_seconds" in row for row in report["rows"])


def test_cli_evaluate_3d_returns_error_without_report_when_provider_config_fails(
    tmp_path,
    monkeypatch,
) -> None:
    prompts_file = tmp_path / "prompts.txt"
    output_file = tmp_path / "report.json"
    prompts_file.write_text("Create a moon cup.\n", encoding="utf-8")

    def raise_provider_error(settings):
        raise MeshyProviderError("MESHY_API_KEY is required.")

    monkeypatch.setattr("myth_forge_api.cli.build_three_d_provider", raise_provider_error)

    exit_code = main(
        [
            "evaluate-3d",
            "--provider",
            "meshy",
            "--prompts-file",
            str(prompts_file),
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 1
    assert not output_file.exists()


class FailingThreeDProvider:
    provider_name = "failing"

    def generate_game_asset(self, request: ThreeDGenerationRequest):
        raise MeshyProviderError("failed Authorization=Bearer test-secret raw=test-secret")


def test_cli_evaluate_3d_sanitizes_per_prompt_errors(tmp_path, monkeypatch) -> None:
    prompts_file = tmp_path / "prompts.txt"
    output_file = tmp_path / "report.json"
    prompts_file.write_text("Create a moon cup.\n", encoding="utf-8")

    monkeypatch.setattr(
        "myth_forge_api.cli.build_three_d_provider",
        lambda settings: FailingThreeDProvider(),
    )

    exit_code = main(
        [
            "evaluate-3d",
            "--provider",
            "local",
            "--prompts-file",
            str(prompts_file),
            "--output",
            str(output_file),
        ]
    )

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)

    assert exit_code == 0
    assert report["rows"][0]["status"] == "failed"
    assert "test-secret" not in report_text
    assert "Authorization" not in report_text
    assert "raw=" not in report_text


def test_cli_provider_handoff_writes_local_report(tmp_path, monkeypatch) -> None:
    output_file = tmp_path / "handoff.json"
    monkeypatch.setattr("myth_forge_api.cli.load_settings", lambda: Settings())

    exit_code = main(["provider-handoff", "--output", str(output_file)])

    assert exit_code == 0
    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert report["kind"] == "provider_handoff_report"
    assert report["mode"] == "configuration"
    assert report["overall_demo_ready"] is True
    assert report["overall_real_ready"] is False
    assert report["core_real_ready"] is False
    assert report["core_provider_kinds"] == ["three_d", "npc", "capture_storage"]
    assert report["missing_env"] == []
    assert "MESHY_API_KEY" in report["backend_only_env"]
    assert "OPENAI_API_KEY" in report["backend_only_env"]
    assert "Provider secrets stay on the backend" in report["mobile_secret_policy"]
    assert any("provider-readiness" in command for command in report["next_commands"])


def test_cli_provider_handoff_require_core_real_returns_two_when_keys_missing(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "handoff.json"
    monkeypatch.setattr(
        "myth_forge_api.cli.load_settings",
        lambda: Settings(three_d_provider="meshy", npc_provider="openai"),
    )

    exit_code = main(["provider-handoff", "--require-core-real", "--output", str(output_file)])

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)
    assert exit_code == 2
    assert report["core_real_ready"] is False
    assert report["missing_env"] == ["MESHY_API_KEY", "OPENAI_API_KEY"]
    assert "sk-" not in report_text


def test_cli_provider_handoff_core_real_ready_with_keys_without_secret_leak(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "handoff.json"
    monkeypatch.setattr(
        "myth_forge_api.cli.load_settings",
        lambda: Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-secret",
            npc_provider="openai",
            openai_api_key="sk-openai-secret",
        ),
    )

    exit_code = main(["provider-handoff", "--require-core-real", "--output", str(output_file)])

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)
    assert exit_code == 0
    assert report["core_real_ready"] is True
    assert report["overall_real_ready"] is False
    assert report["missing_env"] == []
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text


def test_cli_provider_handoff_prints_json_to_stdout(capsys, monkeypatch) -> None:
    monkeypatch.setattr("myth_forge_api.cli.load_settings", lambda: Settings())

    exit_code = main(["provider-handoff"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["kind"] == "provider_handoff_report"


def test_cli_demo_acceptance_writes_report(tmp_path, monkeypatch) -> None:
    output_file = tmp_path / "acceptance.json"
    calls = []

    def fake_run_demo_acceptance(**kwargs):
        calls.append(kwargs)
        return DemoAcceptanceResult(
            exit_code=0,
            report={
                "kind": "demo_acceptance_report",
                "mode": kwargs["provider_mode"],
                "status": "succeeded",
            },
        )

    monkeypatch.setattr("myth_forge_api.cli.run_demo_acceptance", fake_run_demo_acceptance)

    exit_code = main(
        [
            "demo-acceptance",
            "--provider-mode",
            "local",
            "--npc-steps",
            "3",
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 0
    assert calls == [
        {
            "provider_mode": "local",
            "npc_steps": 3,
            "require_real_core": False,
        }
    ]
    assert json.loads(output_file.read_text(encoding="utf-8"))["kind"] == (
        "demo_acceptance_report"
    )


def test_cli_demo_acceptance_prints_stdout_and_returns_result_code(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        "myth_forge_api.cli.run_demo_acceptance",
        lambda **kwargs: DemoAcceptanceResult(
            exit_code=2,
            report={
                "kind": "demo_acceptance_report",
                "mode": kwargs["provider_mode"],
                "status": "not_ready",
            },
        ),
    )

    exit_code = main(["demo-acceptance", "--provider-mode", "configured", "--require-real-core"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert payload["kind"] == "demo_acceptance_report"
    assert payload["mode"] == "configured"
    assert payload["status"] == "not_ready"


@pytest.mark.parametrize("npc_steps", ["-1", "4"])
def test_cli_demo_acceptance_rejects_invalid_npc_steps(npc_steps: str) -> None:
    with pytest.raises(SystemExit):
        main(["demo-acceptance", "--npc-steps", npc_steps])
