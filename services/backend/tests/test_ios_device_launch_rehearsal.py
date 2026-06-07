import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from myth_forge_api.ios_device_launch_rehearsal import (
    build_ios_device_launch_rehearsal_report,
)
from myth_forge_api.ios_device_launch_rehearsal_readiness import (
    build_ios_device_launch_rehearsal_readiness_report,
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
    local_sources = {
        source["id"]: source
        for source in result.report["local_rehearsal_reports"]
    }
    assert local_sources["visual_regression"]["status"] == "ready"
    assert local_sources["visual_regression"]["path"] == (
        "services/backend/.local/visual-regression-local.json"
    )
    assert local_sources["visual_regression"]["command"] == "make visual-regression-local"
    assert result.report["summary"]["partial"] >= 1
    assert result.report["summary"]["missing"] == 0
    assert result.report["summary"]["blocked"] == 0
    assert result.report["operator_actions"][0] == "continue with make backend-device-demo"
    assert (
        result.report["operator_actions"][1]
        == "run make mobile-deploy-preflight after backend is running"
    )
    assert "run make ios-device-launch-rehearsal" not in result.report["operator_actions"]
    assert "configured" in report_text
    assert str(tmp_path) not in report_text


def test_ios_device_launch_rehearsal_routes_blocked_saved_report_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    local_dir = repo_root / "services/backend/.local"
    local_dir.mkdir(parents=True)
    _write_local_rehearsal_reports(local_dir)
    _write_json(
        local_dir / "final-configured-preflight.json",
        {
            "kind": "final_configured_preflight_report",
            "status": "blocked",
            "operator_actions": [
                "fill services/backend/.local/final-resources.env",
                "run make final-resource-apply-preview",
            ],
        },
    )
    _write_json(
        local_dir / "final-handoff-index.json",
        {"kind": "final_handoff_index_report", "status": "ready"},
    )
    _write_json(
        local_dir / "ios-device-launch-certificate.json",
        {
            "kind": "ios_device_launch_certificate_report",
            "status": "ready",
            "mode": "local",
            "summary": {"ready": 4, "manual": 0, "live": 0, "partial": 0},
            "safety": {
                "provider_calls": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
            },
        },
    )

    result = build_ios_device_launch_rehearsal_report(repo_root=repo_root)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["operator_actions"][0] == (
        "final_configured_preflight: fill services/backend/.local/final-resources.env"
    )
    assert "run make ios-device-launch-rehearsal" not in result.report["operator_actions"]
    assert (
        "final_configured_preflight: run make final-resource-apply-preview"
        in result.report["operator_actions"]
    )


def test_ios_device_launch_rehearsal_routes_local_rehearsal_source_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    local_dir = repo_root / "services/backend/.local"
    local_dir.mkdir(parents=True)
    _write_local_rehearsal_reports(local_dir)
    _write_json(
        local_dir / "ios-deploy-runbook-local.json",
        {
            "kind": "ios_deploy_runbook_report",
            "mode": "local",
            "status": "blocked",
            "operator_actions": [
                "provide iOS deploy config and rerun mobile deploy preflight",
                "resolve Xcode build gate outside the app",
            ],
        },
    )
    _write_json(
        local_dir / "final-configured-preflight.json",
        {"kind": "final_configured_preflight_report", "status": "ready"},
    )
    _write_json(
        local_dir / "final-handoff-index.json",
        {"kind": "final_handoff_index_report", "status": "ready"},
    )
    _write_json(
        local_dir / "ios-device-launch-certificate.json",
        {
            "kind": "ios_device_launch_certificate_report",
            "status": "ready",
            "mode": "local",
            "summary": {"ready": 4, "manual": 0, "live": 0, "partial": 0},
            "safety": {
                "provider_calls": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
            },
        },
    )

    result = build_ios_device_launch_rehearsal_report(repo_root=repo_root)
    sequence = {step["id"]: step for step in result.report["sequence"]}

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert sequence["final_rehearsal_local"]["operator_actions"] == [
        (
            "ios_deploy_runbook_local: provide iOS deploy config and rerun "
            "mobile deploy preflight"
        ),
        "ios_deploy_runbook_local: resolve Xcode build gate outside the app",
    ]
    assert result.report["operator_actions"][0] == (
        "final_rehearsal_local: ios_deploy_runbook_local: provide iOS deploy "
        "config and rerun mobile deploy preflight"
    )
    assert (
        "review final_rehearsal_local: make final-rehearsal-local"
        not in result.report["operator_actions"]
    )


def test_ios_device_launch_rehearsal_normalizes_legacy_final_resource_copy_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    local_dir = repo_root / "services/backend/.local"
    local_dir.mkdir(parents=True)
    _write_local_rehearsal_reports(local_dir)
    _write_json(
        local_dir / "ios-deploy-runbook-local.json",
        {
            "kind": "ios_deploy_runbook_report",
            "mode": "local",
            "status": "blocked",
            "operator_actions": [
                (
                    "copy services/backend/final-resources.env.example to "
                    "services/backend/.local/final-resources.env"
                ),
                "provide iOS deploy config and rerun mobile deploy preflight",
            ],
        },
    )
    _write_json(
        local_dir / "final-configured-preflight.json",
        {
            "kind": "final_configured_preflight_report",
            "status": "blocked",
            "operator_actions": [
                (
                    "copy services/backend/final-resources.env.example to "
                    "services/backend/.local/final-resources.env"
                ),
                "make final-apply-resources",
            ],
        },
    )
    _write_json(
        local_dir / "final-handoff-index.json",
        {"kind": "final_handoff_index_report", "status": "ready"},
    )
    _write_json(
        local_dir / "ios-device-launch-certificate.json",
        {
            "kind": "ios_device_launch_certificate_report",
            "status": "ready",
            "mode": "local",
            "summary": {"ready": 4, "manual": 0, "live": 0, "partial": 0},
            "safety": {
                "provider_calls": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
            },
        },
    )

    result = build_ios_device_launch_rehearsal_report(repo_root=repo_root)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert "run make final-resource-init" in result.report["operator_actions"]
    assert "services/backend/final-resources.env.example" not in report_text
    assert (
        "final_rehearsal_local: ios_deploy_runbook_local: provide iOS deploy "
        "config and rerun mobile deploy preflight"
    ) in result.report["operator_actions"]
    assert (
        "final_configured_preflight: make final-apply-resources"
        in result.report["operator_actions"]
    )


def test_ios_device_launch_rehearsal_routes_final_acceptance_source_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    local_dir = repo_root / "services/backend/.local"
    local_dir.mkdir(parents=True)
    _write_local_rehearsal_reports(local_dir)
    _write_json(
        local_dir / "final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 2, "failed": 0},
            "operator_actions": [
                "provide iOS deploy config and rerun mobile deploy preflight",
                "resolve Xcode build gate outside the app",
            ],
        },
    )
    _write_json(
        local_dir / "final-configured-preflight.json",
        {"kind": "final_configured_preflight_report", "status": "ready"},
    )
    _write_json(
        local_dir / "final-handoff-index.json",
        {"kind": "final_handoff_index_report", "status": "ready"},
    )
    _write_json(
        local_dir / "ios-device-launch-certificate.json",
        {
            "kind": "ios_device_launch_certificate_report",
            "status": "ready",
            "mode": "local",
            "summary": {"ready": 4, "manual": 0, "live": 0, "partial": 0},
            "safety": {
                "provider_calls": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
            },
        },
    )

    result = build_ios_device_launch_rehearsal_report(repo_root=repo_root)
    sequence = {step["id"]: step for step in result.report["sequence"]}

    assert result.exit_code == 2
    assert sequence["final_rehearsal_local"]["operator_actions"][:2] == [
        (
            "final_acceptance_local: provide iOS deploy config and rerun "
            "mobile deploy preflight"
        ),
        "final_acceptance_local: resolve Xcode build gate outside the app",
    ]
    assert result.report["operator_actions"][0] == (
        "final_rehearsal_local: final_acceptance_local: provide iOS deploy "
        "config and rerun mobile deploy preflight"
    )
    assert (
        "final_rehearsal_local: review final_acceptance_local: make final-acceptance-local"
        not in result.report["operator_actions"]
    )


def test_ios_device_launch_rehearsal_preserves_final_handoff_source_freshness(
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
            "status": "blocked",
            "summary": {"ready": 1, "blocked": 1, "live": 1},
            "freshness_summary": {"fresh": 4, "stale": 1, "unknown": 0},
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
    sequence = {step["id"]: step for step in result.report["sequence"]}
    final_handoff_step = sequence["final_handoff_index"]

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert final_handoff_step["status"] == "blocked"
    assert final_handoff_step["freshness_summary"] == {
        "fresh": 4,
        "stale": 1,
        "unknown": 0,
    }
    assert final_handoff_step["freshness_status"] == "stale"
    assert final_handoff_step["freshness_classification"] == "stale_report"


def test_ios_device_launch_rehearsal_routes_handoff_and_certificate_actions(
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
            "status": "blocked",
            "operator_actions": ["run make final-configured-preflight"],
        },
    )
    _write_json(
        local_dir / "ios-device-launch-certificate.json",
        {
            "kind": "ios_device_launch_certificate_report",
            "status": "blocked",
            "mode": "local",
            "operator_actions": ["run make final-handoff-index"],
        },
    )

    result = build_ios_device_launch_rehearsal_report(repo_root=repo_root)

    assert result.exit_code == 2
    assert (
        "final_handoff_index: run make final-configured-preflight"
        in result.report["operator_actions"]
    )
    assert (
        "ios_device_launch_certificate: run make final-handoff-index"
        in result.report["operator_actions"]
    )
    assert "review final_handoff_index: make final-handoff-index" not in result.report[
        "operator_actions"
    ]
    assert (
        "review ios_device_launch_certificate: make ios-device-launch-certificate"
        not in result.report["operator_actions"]
    )


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


def test_ios_device_launch_rehearsal_readiness_missing_file_has_unknown_freshness(
    tmp_path: Path,
) -> None:
    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["status"] == "missing"
    assert result.report["freshness"] == {
        "status": "unknown",
        "classification": "source_missing",
        "checked_against": "git_head",
        "source_modified_at": None,
        "current_revision": None,
        "current_revision_committed_at": None,
    }


def test_ios_device_launch_rehearsal_readiness_marks_saved_report_fresh_against_git_head(
    tmp_path: Path,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-07T12:00:00+00:00",
    )
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="ready")
    _set_mtime(report_path, "2026-06-07T12:05:00+00:00")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["freshness"]["status"] == "fresh"
    assert result.report["freshness"]["classification"] == "fresh_report"
    assert result.report["freshness"]["current_revision"]


def test_ios_device_launch_rehearsal_readiness_resolves_relative_repo_root_from_backend_cwd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-07T12:00:00+00:00",
    )
    backend_cwd = repo_root / "services/backend"
    backend_cwd.mkdir(parents=True, exist_ok=True)
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="ready")
    _set_mtime(report_path, "2026-06-07T12:05:00+00:00")
    monkeypatch.chdir(backend_cwd)

    result = build_ios_device_launch_rehearsal_readiness_report(
        repo_root=Path("../.."),
    )

    assert result.exit_code == 0
    assert result.report["freshness"]["classification"] == "fresh_report"
    assert result.report["freshness"]["checked_against"] == "git_product_sources"
    assert result.report["freshness"]["current_revision"]


def test_ios_device_launch_rehearsal_readiness_blocks_stale_saved_report_against_git_head(
    tmp_path: Path,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-07T12:10:00+00:00",
    )
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="ready")
    _set_mtime(report_path, "2026-06-07T12:00:00+00:00")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["freshness"]["status"] == "stale"
    assert result.report["freshness"]["classification"] == "stale_report"
    assert result.report["blockers"][0]["id"] == "ios_device_launch_rehearsal_freshness"
    assert result.report["blockers"][0]["classification"] == "stale_report"
    assert result.report["operator_actions"][0] == (
        "rerun make ios-device-launch-rehearsal to regenerate "
        "services/backend/.local/ios-device-launch-rehearsal.json for the current product sources"
    )


def test_ios_device_launch_rehearsal_readiness_ignores_newer_docs_only_commit(
    tmp_path: Path,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-07T12:00:00+00:00",
    )
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="ready")
    _set_mtime(report_path, "2026-06-07T12:05:00+00:00")
    _commit_fixture_file(
        repo_root,
        relative_path="docs/superpowers/plans/docs-only.md",
        content="docs only\n",
        committed_at="2026-06-07T12:10:00+00:00",
        message="docs only",
    )

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["freshness"]["status"] == "fresh"
    assert result.report["freshness"]["checked_against"] == "git_product_sources"


def test_ios_device_launch_rehearsal_readiness_preserves_final_handoff_source_freshness(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["sequence"][0]["freshness_summary"] = {
        "fresh": 4,
        "stale": 1,
        "unknown": 0,
    }
    payload["sequence"][0]["freshness_status"] = "stale"
    payload["sequence"][0]["freshness_classification"] = "stale_report"
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)
    row = result.report["sequence"][0]

    assert row["freshness_summary"] == {"fresh": 4, "stale": 1, "unknown": 0}
    assert row["freshness_status"] == "stale"
    assert row["freshness_classification"] == "stale_report"


def test_ios_device_launch_rehearsal_readiness_preserves_bounded_operator_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["operator_actions"] = [
        "final_rehearsal_local: action 1",
        "final_rehearsal_local: action 2",
        "final_rehearsal_local: action 3",
        "final_rehearsal_local: action 4",
        "final_rehearsal_local: action 5",
        "final_rehearsal_local: action 6",
        "final_configured_preflight: action 1",
        "final_configured_preflight: action 2",
        "final_configured_preflight: action 3",
        "final_configured_preflight: action 4",
        "final_handoff_index: run make final-configured-preflight",
        "final_handoff_index: run configured final-demo-launch",
        "final_handoff_index: run make mobile-deploy-preflight",
        "ios_device_launch_certificate: run make final-handoff-index",
        "ios_device_launch_certificate: provide iOS deploy config",
        "ios_device_launch_certificate: run make ios-deploy-runbook-local",
        "ios_device_launch_certificate: start backend-device-demo",
        "future_launch_group: optional action 1",
        "future_launch_group: optional action 2",
        "future_launch_group: optional action 3",
        "future_launch_group: optional action 4",
    ]
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)

    assert result.exit_code == 2
    assert len(result.report["operator_actions"]) == 20
    assert (
        "final_handoff_index: run make final-configured-preflight"
        in result.report["operator_actions"]
    )
    assert (
        "ios_device_launch_certificate: run make final-handoff-index"
        in result.report["operator_actions"]
    )
    assert "future_launch_group: optional action 4" not in result.report["operator_actions"]


def test_ios_device_launch_rehearsal_readiness_normalizes_legacy_copy_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["operator_actions"] = [
        (
            "final_configured_preflight: copy "
            "services/backend/final-resources.env.example to "
            "services/backend/.local/final-resources.env"
        ),
        "final_handoff_index: run make final-configured-preflight",
    ]
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert "run make final-resource-init" in result.report["operator_actions"]
    assert "services/backend/final-resources.env.example" not in report_text
    assert (
        "final_handoff_index: run make final-configured-preflight"
        in result.report["operator_actions"]
    )


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
        local_dir / "visual-regression-local.json",
        {
            "kind": "visual_regression_report",
            "status": "passed",
            "summary": {"passed": 1, "failed": 0},
            "artifacts": [
                {
                    "id": "p0.118_scene_load_proof",
                    "status": "passed",
                }
            ],
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


def _init_git_repo(tmp_path: Path, *, committed_at: str) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    env = os.environ | {
        "GIT_AUTHOR_DATE": committed_at,
        "GIT_COMMITTER_DATE": committed_at,
    }
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_root,
        check=True,
    )
    (repo_root / "README.md").write_text("test\n", encoding="utf-8")
    (repo_root / "Makefile").write_text(
        "backend-test:\n\tpytest\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", "README.md", "Makefile"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_root,
        check=True,
        env=env,
        capture_output=True,
    )
    return repo_root


def _commit_fixture_file(
    repo_root: Path,
    *,
    relative_path: str,
    content: str,
    committed_at: str,
    message: str,
) -> None:
    path = repo_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", relative_path], cwd=repo_root, check=True)
    env = os.environ | {
        "GIT_AUTHOR_DATE": committed_at,
        "GIT_COMMITTER_DATE": committed_at,
    }
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_root,
        check=True,
        env=env,
        capture_output=True,
    )


def _write_saved_rehearsal_readiness_report(
    repo_root: Path,
    *,
    status: str = "ready",
) -> Path:
    report_path = repo_root / "services/backend/.local/ios-device-launch-rehearsal.json"
    _write_json(
        report_path,
        {
            "kind": "ios_device_launch_rehearsal_report",
            "status": status,
            "summary": {
                "ready": 4,
                "missing": 0,
                "blocked": 0,
                "partial": 0,
                "manual": 0,
                "live": 0,
            },
            "sequence": [
                {
                    "id": "final_handoff_index",
                    "label": "Final handoff index",
                    "status": "ready",
                    "command": "make final-handoff-index",
                    "classification": "saved_report",
                }
            ],
            "operator_actions": ["iOS device launch rehearsal is ready"],
            "commands": ["make ios-device-launch-rehearsal"],
            "safety": {
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "raw_media_in_report": False,
                "payment_links_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )
    return report_path


def _set_mtime(path: Path, iso_timestamp: str) -> None:
    epoch = datetime.fromisoformat(iso_timestamp).timestamp()
    os.utime(path, (epoch, epoch))
