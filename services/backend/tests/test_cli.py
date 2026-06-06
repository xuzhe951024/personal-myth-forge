import json

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
