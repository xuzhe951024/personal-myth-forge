import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import myth_forge_api.ios_device_launch_rehearsal as ios_device_launch_rehearsal
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
    assert result.report["first_blocker"] == {
        "id": "final_rehearsal_local",
        "label": "Local final rehearsal",
        "status": "missing",
        "classification": "step_missing",
        "command": "make final-rehearsal-local",
        "detail": "run make ios-device-launch-rehearsal",
    }
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "command": "make final-rehearsal-local",
        "source": "first_blocker",
        "validation_command": "make ios-device-launch-rehearsal",
    }
    assert result.report["sequence"][0]["id"] == "final_rehearsal_local"
    assert sequence["final_rehearsal_local"]["detail"] == (
        "run make ios-device-launch-rehearsal"
    )
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
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
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
    assert result.report["operator_actions"] == [
        "start backend-device-demo before device checks: make backend-device-demo; "
        "rerun make mobile-deploy-preflight"
    ]
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
        "fill services/backend/.local/final-resources.env"
    )
    assert "run make ios-device-launch-rehearsal" not in result.report["operator_actions"]
    assert (
        "make final-resource-apply-preview"
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
        local_dir / "mobile-deploy-preflight-evidence.json",
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "blocked",
            "operator_actions": [
                "start backend-device-demo and rerun mobile deploy preflight"
            ],
            "summary": {"blocked": 1},
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
    assert result.report["first_blocker"]["id"] == "final_rehearsal_local"
    expected_runbook_action = (
        "ios_deploy_runbook_local: provide iOS deploy config in "
        "Deployment.local.xcconfig; rerun make mobile-deploy-preflight"
    )
    assert result.report["first_blocker"]["detail"] == (
        f"final_rehearsal_local: {expected_runbook_action}"
    )
    assert sequence["final_rehearsal_local"]["operator_actions"] == [
        expected_runbook_action,
        (
            "ios_deploy_runbook_local: accept the Xcode license outside "
            "Codex, then rerun make mobile-xcode-build-evidence"
        ),
        (
            "mobile_deploy_preflight_evidence: start backend-device-demo before "
            "device checks: make backend-device-demo; rerun make mobile-deploy-preflight"
        ),
    ]
    assert result.report["operator_actions"][0] == expected_runbook_action.removeprefix(
        "ios_deploy_runbook_local: "
    )
    assert not any(
        action.startswith("final_rehearsal_local:")
        for action in result.report["operator_actions"]
    )
    assert (
        "review final_rehearsal_local: make final-rehearsal-local"
        not in result.report["operator_actions"]
    )


def test_ios_device_launch_rehearsal_uses_mobile_preflight_check_details(
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
            "summary": {"passed": 12, "blocked": 2, "failed": 0, "skipped": 0},
            "operator_actions": [
                "start backend-device-demo and rerun mobile deploy preflight",
                "resolve Xcode build gate outside the app",
            ],
        },
    )
    _write_json(
        local_dir / "mobile-deploy-preflight-evidence.json",
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "blocked",
            "operator_actions": [
                "start backend-device-demo and rerun mobile deploy preflight"
            ],
            "checks": [
                {
                    "id": "development_team",
                    "label": "Apple Team ID",
                    "status": "blocked",
                    "detail": "Missing DEVELOPMENT_TEAM",
                },
                {
                    "id": "backend_base_url",
                    "label": "Backend base URL",
                    "status": "blocked",
                    "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
                },
            ],
            "summary": {"blocked": 2},
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
    report_text = json.dumps(result.report)

    expected_detail = (
        "final_rehearsal_local: mobile_deploy_preflight_evidence: "
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    expected_source_action = (
        "mobile_deploy_preflight_evidence: DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto; rerun make mobile-deploy-preflight | "
        "Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    expected_top_level_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    expected_next_action_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["first_blocker"]["detail"] == expected_detail
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "command": expected_next_action_command,
        "source": "operator_actions",
        "validation_command": "make ios-device-launch-rehearsal",
    }
    assert sequence["final_rehearsal_local"]["detail"] == expected_detail
    assert sequence["final_rehearsal_local"]["operator_actions"][0] == (
        expected_source_action
    )
    assert sequence["final_rehearsal_local"]["operator_actions"][1] == (
        "final_acceptance_local: accept the Xcode license outside Codex, then "
        "rerun make mobile-xcode-build-evidence"
    )
    assert result.report["operator_actions"][0] == expected_top_level_action
    assert not any(
        action.startswith("final_rehearsal_local:")
        for action in result.report["operator_actions"]
    )
    assert "start backend-device-demo and rerun mobile deploy preflight" not in (
        result.report["operator_actions"][0]
    )
    assert "MESHY_API_KEY" not in report_text


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
    assert "make final-resource-init" in result.report["operator_actions"]
    assert "services/backend/final-resources.env.example" not in report_text
    assert (
        "provide iOS deploy config in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) in result.report["operator_actions"]
    assert "make final-apply-resources" in result.report["operator_actions"]


def test_ios_device_launch_rehearsal_adds_validation_to_resource_actions(
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
                "provide MESHY_API_KEY in final-resources.env",
                "provide OPENAI_API_KEY in final-resources.env",
                "provide DEVELOPMENT_TEAM in final-resources.env",
                "provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env",
            ],
        },
    )
    _write_json(
        local_dir / "final-configured-preflight.json",
        {
            "kind": "final_configured_preflight_report",
            "status": "blocked",
            "operator_actions": [
                "provide MESHY_API_KEY in final-resources.env",
                "provide OPENAI_API_KEY in final-resources.env",
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
    actions = result.report["operator_actions"]

    assert (
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide OPENAI_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide DEVELOPMENT_TEAM in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert not any(
        action.endswith("provide MESHY_API_KEY in final-resources.env")
        or action.endswith("provide OPENAI_API_KEY in final-resources.env")
        or action.endswith("provide DEVELOPMENT_TEAM in final-resources.env")
        or action.endswith("provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env")
        for action in actions
    )


def test_ios_device_launch_rehearsal_adds_mobile_validation_to_ios_config_actions(
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
                "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL",
            ],
        },
    )
    _write_json(
        local_dir / "final-configured-preflight.json",
        {
            "kind": "final_configured_preflight_report",
            "status": "blocked",
            "operator_actions": [
                "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig",
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
    actions = result.report["operator_actions"]

    assert (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert (
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert not any(
        action.endswith("provide DEVELOPMENT_TEAM in Deployment.local.xcconfig")
        or action.endswith("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
        or action.endswith(
            "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig"
        )
        for action in actions
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
    expected_acceptance_action = (
        "final_acceptance_local: provide iOS deploy config in "
        "Deployment.local.xcconfig; rerun make mobile-deploy-preflight"
    )

    assert result.exit_code == 2
    assert sequence["final_rehearsal_local"]["operator_actions"][:2] == [
        expected_acceptance_action,
        (
            "final_acceptance_local: accept the Xcode license outside Codex, "
            "then rerun make mobile-xcode-build-evidence"
        ),
    ]
    assert result.report["operator_actions"][0] == expected_acceptance_action.removeprefix(
        "final_acceptance_local: "
    )
    assert not any(
        action.startswith("final_rehearsal_local:")
        for action in result.report["operator_actions"]
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
    sequence = {step["id"]: step for step in result.report["sequence"]}

    assert result.exit_code == 2
    assert sequence["final_handoff_index"]["detail"] == (
        "final_handoff_index: make final-configured-preflight; "
        "rerun make configured-live-evidence-bundle"
    )
    assert (
        "make final-configured-preflight; rerun make configured-live-evidence-bundle"
        in result.report["operator_actions"]
    )
    assert "make final-handoff-index" in result.report["operator_actions"]
    assert not any(
        action.startswith("final_handoff_index:")
        or action.startswith("ios_device_launch_certificate:")
        for action in result.report["operator_actions"]
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


def test_ios_device_launch_rehearsal_readiness_cli_writes_report_and_makefile_target(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    output_path = tmp_path / "ios-device-launch-rehearsal-readiness.json"

    from myth_forge_api.cli import main

    exit_code = main(
        [
            "ios-device-launch-rehearsal-readiness",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 2
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["kind"] == "ios_device_launch_rehearsal_readiness_report"
    assert payload["status"] == "missing"

    makefile = (Path(__file__).resolve().parents[3] / "Makefile").read_text(
        encoding="utf-8"
    )
    assert "ios-device-launch-rehearsal-readiness:" in makefile
    assert (
        "services/backend/scripts/write_ios_device_launch_rehearsal_readiness.sh"
        in makefile
    )


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
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None


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


def test_ios_device_launch_rehearsal_readiness_preserves_saved_sequence_actions_when_stale(
    tmp_path: Path,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-07T12:10:00+00:00",
    )
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["sequence"][0]["status"] = "blocked"
    payload["sequence"][0]["operator_actions"] = [
        (
            "mobile_deploy_preflight_evidence: DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; rerun make mobile-deploy-preflight | "
            "Missing DEVELOPMENT_TEAM; "
            "PMF_BACKEND_BASE_URL must be iPhone-reachable"
        )
    ]
    report_path.write_text(json.dumps(payload), encoding="utf-8")
    _set_mtime(report_path, "2026-06-07T12:00:00+00:00")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)
    sequence_row = result.report["sequence"][0]
    first_action = result.report["device_action_bundle"]["first_action"]

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["freshness"]["status"] == "stale"
    assert result.report["next_action"]["command"] == (
        "rerun make ios-device-launch-rehearsal to regenerate "
        "services/backend/.local/ios-device-launch-rehearsal.json for the current "
        "product sources"
    )
    assert sequence_row["operator_actions"] == [
        (
            "mobile_deploy_preflight_evidence: DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; rerun make mobile-deploy-preflight | "
            "Missing DEVELOPMENT_TEAM; "
            "PMF_BACKEND_BASE_URL must be iPhone-reachable"
        )
    ]
    assert first_action["command"] == result.report["next_action"]["command"]
    assert first_action["saved_next_action"] == {
        "id": "final_handoff_index",
        "label": "Final handoff index",
        "status": "blocked",
        "command": (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        ),
        "detail": (
            "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be "
            "iPhone-reachable"
        ),
        "source": "saved_sequence_operator_actions",
        "validation_command": "make ios-device-launch-rehearsal",
    }


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


def test_ios_device_launch_rehearsal_readiness_preserves_sequence_detail(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["sequence"][0]["detail"] = (
        "Final handoff index is stale; rerun safe refresh."
    )
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)

    assert result.report["sequence"][0]["detail"] == (
        "Final handoff index is stale; rerun safe refresh."
    )


def test_ios_device_launch_rehearsal_readiness_exposes_first_blocker_and_next_action(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["sequence"][0]["status"] = "blocked"
    payload["sequence"][0]["detail"] = (
        "final_handoff_index: DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto"
    )
    payload["operator_actions"] = [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; rerun make mobile-deploy-preflight "
            "| Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable"
        )
    ]
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)

    assert result.exit_code == 2
    blocker = result.report["first_blocker"]
    assert blocker["id"] == "final_handoff_index"
    assert blocker["status"] == "blocked"
    assert blocker["source"] == "sequence"
    assert blocker["command"] == "make final-handoff-index"
    assert "DEVELOPMENT_TEAM=YOUR_TEAM_ID" in blocker["detail"]
    assert result.report["operator_actions"][0] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto; rerun make mobile-deploy-preflight "
        "| Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    assert result.report["next_action"] == {
        **blocker,
        "source": "first_blocker",
        "command": (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; rerun make mobile-deploy-preflight"
        ),
    }


def test_ios_device_launch_rehearsal_readiness_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["summary"] = {"ready": 1, "blocked": 1, "manual": 1}
    payload["sequence"] = [
        {
            "id": "final_rehearsal_local",
            "label": "Local final rehearsal",
            "status": "blocked",
            "classification": "saved_report_set",
            "command": "make final-rehearsal-local",
            "detail": "mobile deploy preflight still blocked",
        },
        {
            "id": "ios_device_launch_certificate",
            "label": "iOS device launch certificate",
            "status": "ready",
            "classification": "saved_report_ready",
            "command": "make ios-device-launch-certificate",
        },
    ]
    payload["operator_actions"] = [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; rerun make mobile-deploy-preflight"
        )
    ]
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)
    bundle = result.report["device_action_bundle"]

    assert bundle["id"] == "ios_device_launch_rehearsal_readiness_actions"
    assert bundle["status"] == "blocked"
    assert bundle["source_report"] == "ios_device_launch_rehearsal_readiness"
    assert bundle["summary"]["actions"] == 2
    assert bundle["summary"]["blocked"] == 1
    assert bundle["first_action"]["id"] == "final_rehearsal_local"
    assert bundle["first_action"]["command"] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto; rerun make mobile-deploy-preflight"
    )
    assert bundle["first_action"]["validation_command"] == (
        "make ios-device-launch-rehearsal"
    )
    assert bundle["first_action"]["next_action"]["source"] == "device_action_bundle"
    assert bundle["safety"]["commands_run"] is False
    assert bundle["safety"]["provider_calls"] is False
    assert bundle["safety"]["xcode_or_signing"] is False


def test_ios_device_launch_rehearsal_readiness_sanitizes_sequence_detail(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["sequence"][0]["detail"] = (
        f"detail sk-test {repo_root}/private file:///tmp/private "
        "local-capture://cap https://checkout.example/pay Bearer token"
    )
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)
    report_text = json.dumps(result.report)

    assert "[redacted]" in report_text
    assert "[repo-root]" in report_text
    assert "sk-test" not in report_text
    assert str(repo_root) not in report_text
    assert "file:///" not in report_text
    assert "local-capture://" not in report_text
    assert "checkout.example" not in report_text
    assert "Bearer" not in report_text


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
        "final_handoff_index: make final-configured-preflight; "
        "rerun make configured-live-evidence-bundle"
        in result.report["operator_actions"]
    )
    assert (
        "ios_device_launch_certificate: make final-handoff-index"
        in result.report["operator_actions"]
    )
    assert (
        "ios_device_launch_certificate: make ios-deploy-runbook-local"
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
        "final_handoff_index: make final-configured-preflight; "
        "rerun make configured-live-evidence-bundle"
        in result.report["operator_actions"]
    )


def test_ios_device_launch_rehearsal_readiness_adds_validation_to_saved_resource_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["operator_actions"] = [
        (
            "final_rehearsal_local: ios_deploy_runbook_local: "
            "provide MESHY_API_KEY in final-resources.env"
        ),
        (
            "final_configured_preflight: "
            "provide OPENAI_API_KEY in final-resources.env"
        ),
    ]
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)
    actions = result.report["operator_actions"]

    assert (
        "final_rehearsal_local: ios_deploy_runbook_local: "
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "final_configured_preflight: "
        "provide OPENAI_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert not any(
        action.endswith("provide MESHY_API_KEY in final-resources.env")
        or action.endswith("provide OPENAI_API_KEY in final-resources.env")
        for action in actions
    )


def test_ios_device_launch_rehearsal_readiness_adds_mobile_validation_to_saved_ios_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["operator_actions"] = [
        (
            "final_rehearsal_local: ios_deploy_runbook_local: "
            "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig"
        ),
        (
            "final_rehearsal_local: ios_deploy_runbook_local: "
            "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
        ),
    ]
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)
    actions = result.report["operator_actions"]

    assert (
        "final_rehearsal_local: ios_deploy_runbook_local: "
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert (
        "final_rehearsal_local: ios_deploy_runbook_local: "
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert not any(
        action.endswith("provide DEVELOPMENT_TEAM in Deployment.local.xcconfig")
        or action.endswith("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
        for action in actions
    )


def test_ios_device_launch_rehearsal_prefers_writer_over_old_team_action(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["operator_actions"] = [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        ),
        (
            "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
            "rerun make mobile-deploy-preflight"
        ),
    ]
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)
    actions = result.report["operator_actions"]

    assert actions == [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        )
    ]


def test_ios_device_launch_rehearsal_prefers_writer_over_generic_ios_config_action(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["operator_actions"] = [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        ),
        (
            "provide iOS deploy config in Deployment.local.xcconfig; "
            "rerun make mobile-deploy-preflight"
        ),
    ]
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)
    actions = result.report["operator_actions"]

    assert actions == [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        )
    ]


def test_ios_device_launch_rehearsal_full_actions_prefer_writer_over_generic_ios_config() -> None:
    actions = ios_device_launch_rehearsal._operator_actions(
        [
            {
                "id": "final_rehearsal_local",
                "label": "Local final rehearsal",
                "status": "blocked",
                "command": "make final-rehearsal-local",
                "operator_actions": [
                    (
                        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                        "make mobile-write-deploy-config-auto; "
                        "rerun make mobile-deploy-preflight"
                    ),
                    (
                        "provide iOS deploy config in Deployment.local.xcconfig; "
                        "rerun make mobile-deploy-preflight"
                    ),
                ],
            }
        ]
    )

    assert actions == [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        )
    ]


def test_ios_device_launch_rehearsal_full_actions_prioritize_provider_and_print_handoff() -> None:
    actions = ios_device_launch_rehearsal._operator_actions(
        [
            {
                "id": "final_rehearsal_local",
                "label": "Local final rehearsal",
                "status": "blocked",
                "command": "make final-rehearsal-local",
                "operator_actions": [
                    (
                        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                        "make mobile-write-deploy-config-auto; "
                        "rerun make mobile-deploy-preflight"
                    ),
                    (
                        "accept the Xcode license outside Codex, then rerun "
                        "make mobile-xcode-build-evidence"
                    ),
                    (
                        "provide MESHY_API_KEY in final-resources.env; "
                        "rerun make final-resources-preflight"
                    ),
                    (
                        "provide OPENAI_API_KEY in final-resources.env; "
                        "rerun make final-resources-preflight"
                    ),
                ],
            },
            {
                "id": "final_handoff_index",
                "label": "Final handoff index",
                "status": "blocked",
                "command": "make final-handoff-index",
                "operator_actions": [
                    "make final-configured-preflight",
                    "make final-demo-launch-configured",
                    "make provider-handoff; rerun make live-provider-evidence",
                    (
                        "after explicit Treatstock cost consent, save a sanitized "
                        "services/backend/.local/print-quote-configured.json from "
                        "POST /v1/print-quotes; rerun "
                        "make print-fulfillment-readiness"
                    ),
                ],
            },
        ],
    )

    provider_action = "make provider-handoff; rerun make live-provider-evidence"
    print_action = (
        "after explicit Treatstock cost consent, save a sanitized "
        "services/backend/.local/print-quote-configured.json from POST "
        "/v1/print-quotes; rerun make print-fulfillment-readiness"
    )

    assert actions[0] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    assert provider_action in actions
    assert print_action in actions
    assert actions.index(provider_action) < actions.index(print_action)
    assert actions.index(print_action) < actions.index(
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )


def test_ios_device_launch_rehearsal_local_actions_include_partial_final_demo_handoff() -> None:
    actions = ios_device_launch_rehearsal._local_rehearsal_operator_actions(
        [
            {
                "id": "mobile_deploy_preflight_evidence",
                "status": "blocked",
                "detail": (
                    "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be "
                    "iPhone-reachable"
                ),
                "operator_actions": [
                    (
                        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                        "make mobile-write-deploy-config-auto; "
                        "rerun make mobile-deploy-preflight"
                    )
                ],
            },
            {
                "id": "final_demo_launch_local",
                "status": "partial",
                "operator_actions": [
                    (
                        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                        "make mobile-write-deploy-config-auto; "
                        "rerun make mobile-deploy-preflight"
                    ),
                    "make provider-handoff; rerun make live-provider-evidence",
                    (
                        "after explicit Treatstock cost consent, save a sanitized "
                        "services/backend/.local/print-quote-configured.json from "
                        "POST /v1/print-quotes; rerun "
                        "make print-fulfillment-readiness"
                    ),
                    (
                        "start backend-device-demo before device checks: "
                        "make backend-device-demo; rerun make mobile-deploy-preflight"
                    ),
                    (
                        "provide MESHY_API_KEY in final-resources.env; "
                        "rerun make final-resources-preflight"
                    ),
                ],
            },
        ],
    )

    assert actions == [
        (
            "mobile_deploy_preflight_evidence: DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; rerun "
            "make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM; "
            "PMF_BACKEND_BASE_URL must be iPhone-reachable"
        ),
        (
            "final_demo_launch_local: make provider-handoff; "
            "rerun make live-provider-evidence"
        ),
        (
            "final_demo_launch_local: after explicit Treatstock cost consent, "
            "save a sanitized "
            "services/backend/.local/print-quote-configured.json from POST "
            "/v1/print-quotes; rerun make print-fulfillment-readiness"
        ),
        (
            "final_demo_launch_local: start backend-device-demo before "
            "device checks: make backend-device-demo; rerun "
            "make mobile-deploy-preflight"
        ),
    ]


def test_ios_device_launch_rehearsal_dedupes_duplicate_deploy_writer_roots(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    report_path = _write_saved_rehearsal_readiness_report(repo_root, status="blocked")
    bare_writer = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    detailed_writer = (
        f"{bare_writer} | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["operator_actions"] = [bare_writer, detailed_writer]
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_ios_device_launch_rehearsal_readiness_report(repo_root=repo_root)

    assert result.report["operator_actions"] == [detailed_writer]


def test_ios_device_launch_rehearsal_full_actions_dedupes_deploy_writer_roots() -> None:
    bare_writer = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    detailed_writer = (
        f"{bare_writer} | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )

    actions = ios_device_launch_rehearsal._operator_actions(
        [
            {
                "id": "final_rehearsal_local",
                "label": "Local final rehearsal",
                "status": "blocked",
                "command": "make final-rehearsal-local",
                "operator_actions": [bare_writer, detailed_writer],
            }
        ]
    )

    assert actions == [detailed_writer]


def test_ios_device_launch_rehearsal_sequence_prefers_writer_over_generic_deploy_action(
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
    writer = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    _write_json(
        local_dir / "final-handoff-index.json",
        {
            "kind": "final_handoff_index_report",
            "status": "blocked",
            "operator_actions": [writer],
        },
    )
    _write_json(
        local_dir / "ios-device-launch-certificate.json",
        {
            "kind": "ios_device_launch_certificate_report",
            "status": "blocked",
            "mode": "local",
            "operator_actions": [
                "run make final-handoff-index",
                "provide iOS deploy config and rerun mobile deploy preflight",
                "run make ios-deploy-runbook-local",
            ],
        },
    )

    result = build_ios_device_launch_rehearsal_report(repo_root=repo_root)
    sequence = {step["id"]: step for step in result.report["sequence"]}

    assert sequence["final_handoff_index"]["operator_actions"] == [writer]
    assert sequence["ios_device_launch_certificate"]["operator_actions"] == [
        "make final-handoff-index",
        "make ios-deploy-runbook-local",
    ]
    assert not any(
        "provide iOS deploy config" in action
        for step in result.report["sequence"]
        for action in step.get("operator_actions", [])
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
    _write_json(
        local_dir / "mobile-deploy-preflight-evidence.json",
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "ready",
            "summary": {"ready": 1, "blocked": 0},
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
