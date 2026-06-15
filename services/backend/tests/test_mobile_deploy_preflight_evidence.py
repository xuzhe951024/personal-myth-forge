from __future__ import annotations

import json
import subprocess
from pathlib import Path

from myth_forge_api.cli import main
from myth_forge_api.mobile_deploy_preflight_evidence import (
    build_mobile_deploy_preflight_evidence_report,
    run_mobile_deploy_preflight_evidence,
)


def test_preflight_evidence_ready_from_success_output(tmp_path: Path) -> None:
    result = build_mobile_deploy_preflight_evidence_report(
        repo_root=tmp_path,
        returncode=0,
        stdout=(
            "iOS deploy preflight passed.\n"
            "Bundle: com.example.personalmythforge\n"
            "Backend: http://192.168.1.10:8080\n"
            "Final launch mode: configured\n"
            "Backend health: ok\n"
        ),
        stderr="",
    )

    checks = {check["id"]: check for check in result.report["checks"]}

    assert result.exit_code == 0
    assert result.report["kind"] == "mobile_deploy_preflight_evidence_report"
    assert result.report["status"] == "ready"
    assert result.report["command"] == "make mobile-deploy-preflight"
    assert checks["deploy_preflight"]["status"] == "ready"
    assert checks["backend_health"]["status"] == "ready"
    assert checks["final_launch_mode"]["status"] == "ready"
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
    assert result.report["operator_actions"] == []
    assert result.report["safety"]["commands_run"] is True
    assert result.report["safety"]["xcode_or_signing"] is False


def test_preflight_evidence_blocks_missing_config_with_actions(tmp_path: Path) -> None:
    result = build_mobile_deploy_preflight_evidence_report(
        repo_root=tmp_path,
        returncode=2,
        stdout="",
        stderr=(
            "Missing DEVELOPMENT_TEAM in Deployment.local.xcconfig.\n"
            "Missing PRODUCT_BUNDLE_IDENTIFIER.\n"
            "Missing PMF_BACKEND_BASE_URL.\n"
        ),
    )
    checks = {check["id"]: check for check in result.report["checks"]}

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert checks["development_team"]["status"] == "blocked"
    assert checks["bundle_identifier"]["status"] == "blocked"
    assert checks["backend_base_url"]["status"] == "blocked"
    assert result.report["first_blocker"] == {
        "id": "development_team",
        "label": "Apple Team ID",
        "status": "blocked",
        "detail": "Missing DEVELOPMENT_TEAM",
    }
    expected_command = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    assert result.report["next_action"] == {
        "id": "development_team",
        "label": "Apple Team ID",
        "status": "blocked",
        "command": expected_command,
        "detail": (
            "Missing DEVELOPMENT_TEAM; Missing PRODUCT_BUNDLE_IDENTIFIER; "
            "Missing PMF_BACKEND_BASE_URL"
        ),
        "validation_command": "make mobile-deploy-preflight",
        "source": "first_blocker",
    }
    assert result.report["operator_actions"] == [
        (
            "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
            "rerun make mobile-deploy-preflight"
        ),
        (
            "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
            "rerun make mobile-deploy-preflight"
        ),
        (
            "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
            "rerun make mobile-deploy-preflight"
        ),
    ]


def test_preflight_evidence_exposes_device_action_bundle_for_blocked_checks(
    tmp_path: Path,
) -> None:
    result = build_mobile_deploy_preflight_evidence_report(
        repo_root=tmp_path,
        returncode=2,
        stdout="",
        stderr=(
            "Missing DEVELOPMENT_TEAM in Deployment.local.xcconfig.\n"
            "Missing PRODUCT_BUNDLE_IDENTIFIER.\n"
            "Missing PMF_BACKEND_BASE_URL.\n"
        ),
    )
    report_text = json.dumps(result.report)

    bundle = result.report["device_action_bundle"]

    assert bundle["id"] == "mobile_deploy_preflight_evidence_actions"
    assert bundle["label"] == "Mobile Deploy Preflight Evidence Actions"
    assert bundle["source_report"] == "mobile_deploy_preflight_evidence"
    assert bundle["status"] == "blocked"
    assert bundle["summary"] == {
        "actions": 3,
        "ready": 0,
        "missing": 0,
        "blocked": 3,
        "manual": 3,
        "provider_calls": 0,
        "global_actions": 0,
        "xcode_or_signing": 0,
    }
    assert bundle["first_action"]["id"] == "development_team"
    expected_command = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    assert bundle["first_action"]["command"] == expected_command
    assert bundle["first_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )
    assert bundle["first_action"]["next_action"]["command"] == expected_command
    assert bundle["safety"]["commands_run"] is True
    assert bundle["safety"]["xcode_or_signing"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_preflight_evidence_suggests_auto_writer_for_team_and_backend_url(
    tmp_path: Path,
) -> None:
    result = build_mobile_deploy_preflight_evidence_report(
        repo_root=tmp_path,
        returncode=2,
        stdout="",
        stderr=(
            "Missing DEVELOPMENT_TEAM in Deployment.local.xcconfig.\n"
            "PMF_BACKEND_BASE_URL must be reachable from iPhone, not loopback.\n"
        ),
    )

    expected_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    assert result.report["next_action"] == {
        "id": "development_team",
        "label": "Apple Team ID",
        "status": "blocked",
        "command": expected_command,
        "detail": "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable",
        "validation_command": "make mobile-deploy-preflight",
        "source": "first_blocker",
    }
    assert result.report["operator_actions"] == [expected_command]
    bundle_actions = {
        action["id"]: action
        for action in result.report["device_action_bundle"]["actions"]
    }
    assert bundle_actions["backend_base_url"]["command"] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto"
    )
    assert bundle_actions["backend_base_url"]["next_action"]["command"] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto"
    )


def test_preflight_evidence_next_action_promotes_validation_aware_writer_command(
    tmp_path: Path,
) -> None:
    result = build_mobile_deploy_preflight_evidence_report(
        repo_root=tmp_path,
        returncode=2,
        stdout="",
        stderr=(
            "Missing DEVELOPMENT_TEAM in Deployment.local.xcconfig.\n"
            "PMF_BACKEND_BASE_URL must be reachable from iPhone, not loopback.\n"
        ),
    )

    expected_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )

    assert result.report["next_action"]["command"] == expected_command
    assert result.report["next_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )
    assert result.report["operator_actions"][0] == expected_command


def test_preflight_evidence_blocks_backend_health_without_leaks(tmp_path: Path) -> None:
    expected_command = (
        "start backend-device-demo before device checks: make backend-device-demo"
    )
    expected_action = (
        f"{expected_command}; rerun make mobile-deploy-preflight"
    )
    result = build_mobile_deploy_preflight_evidence_report(
        repo_root=tmp_path,
        returncode=2,
        stdout="",
        stderr=(
            "Backend health check failed. Start backend-device-demo and verify "
            "PMF_BACKEND_BASE_URL. sk-test /Users/zhexu/private file:///tmp/private "
            "checkout_url Bearer token\n"
        ),
    )
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["checks"][0]["id"] == "backend_health"
    assert result.report["checks"][0]["status"] == "blocked"
    assert result.report["first_blocker"]["id"] == "backend_health"
    assert result.report["next_action"] == {
        "id": "backend_health",
        "label": "Backend health",
        "status": "blocked",
        "command": expected_action,
        "detail": "Backend health check failed",
        "validation_command": "make mobile-deploy-preflight",
        "source": "first_blocker",
    }
    assert result.report["operator_actions"] == [expected_action]
    assert "sk-test" not in report_text
    assert "/Users/" not in report_text
    assert "file://" not in report_text
    assert "checkout" not in report_text
    assert "Bearer" not in report_text


def test_run_preflight_evidence_uses_injected_runner(tmp_path: Path) -> None:
    calls: list[Path] = []

    def runner(repo_root: Path) -> subprocess.CompletedProcess[str]:
        calls.append(repo_root)
        return subprocess.CompletedProcess(
            args=["apps/mobile/ios/scripts/deploy_preflight.sh"],
            returncode=0,
            stdout="iOS deploy preflight passed.\nBackend health: ok\n",
            stderr="",
        )

    result = run_mobile_deploy_preflight_evidence(
        repo_root=tmp_path,
        command_runner=runner,
    )

    assert calls == [tmp_path]
    assert result.exit_code == 0
    assert result.report["status"] == "ready"


def test_cli_writes_mobile_deploy_preflight_evidence_blocked_report(
    tmp_path: Path,
) -> None:
    repo_root = _minimal_preflight_repo(tmp_path)
    output = repo_root / "services/backend/.local/mobile-deploy-preflight-evidence.json"

    exit_code = main(
        [
            "mobile-deploy-preflight-evidence",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output),
        ]
    )
    report = json.loads(output.read_text(encoding="utf-8"))

    assert exit_code == 2
    assert report["kind"] == "mobile_deploy_preflight_evidence_report"
    assert report["status"] == "blocked"
    assert "Missing DEVELOPMENT_TEAM" in " ".join(report["stderr_lines"])
    assert str(tmp_path) not in json.dumps(report)


def test_makefile_exposes_mobile_deploy_preflight_evidence_target() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    text = (repo_root / "Makefile").read_text(encoding="utf-8")
    wrapper = (
        repo_root / "services/backend/scripts/write_mobile_deploy_preflight_evidence.sh"
    ).read_text(encoding="utf-8")

    assert "mobile-deploy-preflight-evidence" in text
    assert "services/backend/scripts/write_mobile_deploy_preflight_evidence.sh" in text
    assert "myth_forge_api.cli mobile-deploy-preflight-evidence" in wrapper
    assert ".local/mobile-deploy-preflight-evidence.json" in wrapper


def _minimal_preflight_repo(tmp_path: Path) -> Path:
    source_root = Path(__file__).resolve().parents[3]
    repo_root = tmp_path / "repo"
    ios_root = repo_root / "apps/mobile/ios"
    (repo_root / "services/backend/.local").mkdir(parents=True)
    (ios_root / "Config").mkdir(parents=True)
    (ios_root / "scripts").mkdir(parents=True)
    for relative_path in (
        "apps/mobile/ios/Config/Deployment.xcconfig",
        "apps/mobile/ios/scripts/deploy_preflight.sh",
    ):
        source = source_root / relative_path
        destination = repo_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return repo_root
