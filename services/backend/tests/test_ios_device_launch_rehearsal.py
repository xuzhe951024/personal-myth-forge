import json
from pathlib import Path

from myth_forge_api.ios_device_launch_rehearsal import (
    build_ios_device_launch_rehearsal_report,
)


def test_ios_device_launch_rehearsal_blocks_missing_reports_without_leaks(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_ios_device_launch_rehearsal_report(repo_root=repo_root)
    report_text = json.dumps(result.report)
    sequence = {step["id"]: step for step in result.report["sequence"]}

    assert result.exit_code == 2
    assert result.report["kind"] == "ios_device_launch_rehearsal_report"
    assert result.report["status"] == "blocked"
    assert result.report["summary"]["missing"] >= 1
    assert result.report["sequence"][0]["id"] == "final_rehearsal_local"
    assert sequence["final_configured_preflight"]["status"] == "missing"
    assert sequence["final_handoff_index"]["status"] == "missing"
    assert sequence["ios_device_launch_certificate"]["status"] == "missing"
    assert "make ios-device-launch-rehearsal" in result.report["commands"]
    assert "make final-rehearsal-local" in result.report["commands"]
    assert "make ios-device-launch-certificate" in result.report["commands"]
    assert result.report["safety"]["report_builder_commands_run"] is False
    assert result.report["safety"]["make_wrapper_runs_commands"] is True
    assert result.report["safety"]["provider_calls"] is False
    assert result.report["safety"]["xcode_or_signing"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_ios_device_launch_rehearsal_partial_when_saved_reports_are_ready_with_manual_gates(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    local_dir = repo_root / "services/backend/.local"
    local_dir.mkdir(parents=True)
    _write_local_rehearsal_reports(local_dir)
    _write_json(
        local_dir / "final-configured-preflight.json",
        {"kind": "final_configured_preflight_report", "status": "ready"},
    )
    _write_json(
        local_dir / "final-handoff-index.json",
        {
            "kind": "final_handoff_index_report",
            "status": "ready",
            "summary": {"ready": 2, "live": 1},
        },
    )
    _write_json(
        local_dir / "ios-device-launch-certificate.json",
        {
            "kind": "ios_device_launch_certificate_report",
            "status": "ready",
            "mode": "configured",
            "summary": {"ready": 4, "manual": 2, "live": 1, "partial": 0},
            "safety": {
                "provider_calls": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
            },
        },
    )

    result = build_ios_device_launch_rehearsal_report(repo_root=repo_root)
    report_text = json.dumps(result.report)

    assert result.exit_code == 0
    assert result.report["status"] == "partial"
    assert result.report["mode"] == "configured"
    assert result.report["configured_preflight"]["status"] == "ready"
    assert result.report["final_handoff_index"]["status"] == "ready"
    assert result.report["ios_device_launch_certificate"]["status"] == "ready"
    assert result.report["summary"]["partial"] >= 1
    assert result.report["summary"]["missing"] == 0
    assert result.report["summary"]["blocked"] == 0
    assert result.report["operator_actions"][0] == "run make ios-device-launch-rehearsal"
    assert "configured" in report_text
    assert str(tmp_path) not in report_text


def test_ios_device_launch_rehearsal_cli_writes_report_and_makefile_target(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    output_path = tmp_path / "ios-device-launch-rehearsal.json"

    from myth_forge_api.cli import main

    exit_code = main(
        [
            "ios-device-launch-rehearsal",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 2
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["kind"] == "ios_device_launch_rehearsal_report"
    assert payload["status"] == "blocked"

    makefile = (Path(__file__).resolve().parents[3] / "Makefile").read_text(
        encoding="utf-8"
    )
    assert "ios-device-launch-rehearsal:" in makefile
    assert "services/backend/scripts/write_ios_device_launch_rehearsal.sh" in makefile


def _write_local_rehearsal_reports(local_dir: Path) -> None:
    _write_json(
        local_dir / "3d-evaluation-local.json",
        {
            "kind": "three_d_evaluation_report",
            "total_cases": 20,
            "succeeded": 20,
            "failed": 0,
        },
    )
    _write_json(
        local_dir / "npc-evaluation-local.json",
        {
            "kind": "npc_agent_evaluation_report",
            "total_cases": 6,
            "succeeded": 6,
            "failed": 0,
        },
    )
    _write_json(
        local_dir / "final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0},
        },
    )
    _write_json(
        local_dir / "final-demo-launch-local.json",
        {
            "kind": "final_demo_launch_report",
            "mode": "local",
            "overall_status": "partial",
            "summary": {"ready": 8, "manual": 1, "blocked": 0},
        },
    )
    _write_json(
        local_dir / "ios-deploy-runbook-local.json",
        {
            "kind": "ios_deploy_runbook_report",
            "mode": "local",
            "status": "partial",
        },
    )


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
