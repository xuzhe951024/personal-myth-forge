from __future__ import annotations

import json
import subprocess
from pathlib import Path

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
    assert result.report["operator_actions"] == [
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig",
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL",
    ]


def test_preflight_evidence_blocks_backend_health_without_leaks(tmp_path: Path) -> None:
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
    assert result.report["operator_actions"] == [
        "start backend-device-demo and rerun mobile deploy preflight"
    ]
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
