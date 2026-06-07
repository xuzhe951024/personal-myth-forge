import json
from pathlib import Path

from myth_forge_api.three_d_evaluation_readiness import (
    build_three_d_evaluation_readiness_report,
)


def test_three_d_evaluation_readiness_missing_file_without_running_commands(
    tmp_path: Path,
) -> None:
    result = build_three_d_evaluation_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["kind"] == "three_d_evaluation_readiness_report"
    assert result.report["status"] == "missing"
    assert result.report["summary"] == {
        "total_cases": 0,
        "succeeded": 0,
        "failed": 0,
    }
    assert result.report["coverage"]["input_modes"]["text_prompt"] == 0
    assert result.report["coverage"]["variant_roles"] == {}
    assert result.report["coverage"]["scene_loadable_cases"] == 0
    assert result.report["blockers"] == []
    assert "evaluate-3d" in result.report["operator_actions"][0]
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["provider_calls"] is False


def test_three_d_evaluation_readiness_ready_report(tmp_path: Path) -> None:
    _write_three_d_evaluation_report(tmp_path, _ready_report())

    result = build_three_d_evaluation_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["summary"] == {
        "total_cases": 20,
        "succeeded": 20,
        "failed": 0,
    }
    assert result.report["coverage"]["input_modes"]["text_prompt"] == 20
    assert result.report["coverage"]["input_modes"]["multi_image"] == 0
    assert result.report["coverage"]["variant_roles"]["game_asset"] == 20
    assert result.report["coverage"]["variant_roles"]["ios_scene_asset"] == 20
    assert result.report["coverage"]["scene_loadable_cases"] == 20
    assert result.report["operator_actions"] == ["3D evaluation is ready"]


def test_three_d_evaluation_readiness_blocks_invalid_json(tmp_path: Path) -> None:
    path = _evaluation_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not-json", encoding="utf-8")

    result = build_three_d_evaluation_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["blockers"][0]["classification"] == "unreadable_report"
    assert "evaluate-3d" in result.report["blockers"][0]["command"]


def test_three_d_evaluation_readiness_blocks_failed_report_and_redacts(
    tmp_path: Path,
) -> None:
    failed_report = _ready_report()
    failed_report["failed"] = 1
    failed_report["cases"] = [
        {
            "case_id": "3d_secret_case",
            "status": "failed",
            "error": (
                "Meshy failed Authorization=Bearer test-secret "
                "raw_context: private text file:///Users/example/private.png "
                "data:image/png;base64,abc123 checkout_url https://pay.example/abc"
            ),
        }
    ]
    _write_three_d_evaluation_report(tmp_path, failed_report)

    result = build_three_d_evaluation_readiness_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["blockers"][0]["classification"] == "three_d_evaluation_failed"
    assert "[redacted]" in report_text or "[withheld]" in report_text
    assert "test-secret" not in report_text
    assert "raw_context:" not in report_text
    assert "/Users/" not in report_text
    assert "file://" not in report_text
    assert "data:image" not in report_text
    assert "checkout_url" not in report_text
    assert "pay.example" not in report_text


def _write_three_d_evaluation_report(repo_root: Path, report: dict[str, object]) -> Path:
    path = _evaluation_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def _evaluation_path(repo_root: Path) -> Path:
    return repo_root / "services/backend/.local/3d-evaluation-local.json"


def _ready_report() -> dict[str, object]:
    return {
        "kind": "three_d_evaluation_report",
        "suite": "default-v0",
        "provider": "local",
        "total_cases": 20,
        "succeeded": 20,
        "failed": 0,
        "coverage": {
            "input_modes": {
                "text_prompt": 20,
                "single_image": 0,
                "multi_image": 0,
                "unknown": 0,
            },
            "variant_roles": {
                "game_asset": 20,
                "ios_scene_asset": 20,
            },
            "scene_loadable_cases": 20,
        },
        "safety": {
            "raw_media_in_report": False,
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
        },
        "cases": [],
    }
