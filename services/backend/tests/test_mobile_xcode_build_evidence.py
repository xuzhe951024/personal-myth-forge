from __future__ import annotations

import json
import subprocess
from pathlib import Path

from myth_forge_api.cli import main
from myth_forge_api.mobile_xcode_build_evidence import (
    build_mobile_xcode_build_evidence_report,
    run_mobile_xcode_build_evidence,
)


def test_xcode_build_evidence_ready_from_success_output(tmp_path: Path) -> None:
    result = build_mobile_xcode_build_evidence_report(
        repo_root=tmp_path,
        returncode=0,
        stdout="** BUILD SUCCEEDED **\n",
        stderr="",
    )
    checks = {check["id"]: check for check in result.report["checks"]}

    assert result.exit_code == 0
    assert result.report["kind"] == "mobile_xcode_build_evidence_report"
    assert result.report["status"] == "ready"
    assert result.report["classification"] == "ready"
    assert result.report["command"] == "make mobile-xcode-build"
    assert checks["xcode_build_gate"]["status"] == "ready"
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
    assert result.report["operator_actions"] == []
    assert result.report["safety"]["commands_run"] is True
    assert result.report["safety"]["xcode_or_signing"] is True
    assert result.report["safety"]["code_signing_allowed"] is False
    assert result.report["safety"]["keychain_writes"] is False
    assert result.report["safety"]["writes_derived_data"] is True


def test_xcode_build_evidence_blocks_unaccepted_license_without_leaks(
    tmp_path: Path,
) -> None:
    result = build_mobile_xcode_build_evidence_report(
        repo_root=tmp_path,
        returncode=69,
        stdout="",
        stderr=(
            "You have not agreed to the Xcode license agreements. "
            "/Users/zhexu/private sk-test file:///tmp/private checkout_url "
            "Bearer token\n"
        ),
    )
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["classification"] == "blocked_by_apple_sdk_license"
    assert result.report["checks"][0]["id"] == "xcode_license"
    assert result.report["checks"][0]["status"] == "blocked"
    assert result.report["operator_actions"] == [
        "accept the Xcode license outside Codex, then rerun make mobile-xcode-build-evidence"
    ]
    assert result.report["first_blocker"] == {
        "id": "xcode_license",
        "label": "Xcode license",
        "status": "blocked",
        "classification": "blocked_by_apple_sdk_license",
        "command": (
            "accept the Xcode license outside Codex, then rerun "
            "make mobile-xcode-build-evidence"
        ),
        "detail": "Apple SDK license agreement is not accepted.",
        "validation_command": "make mobile-xcode-build-evidence",
    }
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "source": "first_blocker",
    }
    assert "sk-test" not in report_text
    assert "/Users/" not in report_text
    assert "file://" not in report_text
    assert "checkout" not in report_text
    assert "Bearer" not in report_text


def test_xcode_build_evidence_exposes_device_action_bundle_for_blocked_gate(
    tmp_path: Path,
) -> None:
    result = build_mobile_xcode_build_evidence_report(
        repo_root=tmp_path,
        returncode=69,
        stdout="",
        stderr="You have not agreed to the Xcode license agreements.\n",
    )
    report_text = json.dumps(result.report)

    bundle = result.report["device_action_bundle"]

    assert bundle["id"] == "mobile_xcode_build_evidence_actions"
    assert bundle["label"] == "Mobile Xcode Build Evidence Actions"
    assert bundle["source_report"] == "mobile_xcode_build_evidence"
    assert bundle["status"] == "blocked"
    assert bundle["summary"] == {
        "actions": 1,
        "ready": 0,
        "missing": 0,
        "blocked": 1,
        "manual": 1,
        "provider_calls": 0,
        "global_actions": 1,
        "xcode_or_signing": 1,
    }
    assert bundle["first_action"]["id"] == "xcode_license"
    assert bundle["first_action"]["command"] == (
        "accept the Xcode license outside Codex, then rerun "
        "make mobile-xcode-build-evidence"
    )
    assert bundle["first_action"]["validation_command"] == (
        "make mobile-xcode-build-evidence"
    )
    assert bundle["first_action"]["next_action"]["command"] == (
        "accept the Xcode license outside Codex, then rerun "
        "make mobile-xcode-build-evidence"
    )
    assert bundle["safety"]["commands_run"] is True
    assert bundle["safety"]["xcode_or_signing"] is True
    assert bundle["safety"]["code_signing_allowed"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_xcode_build_evidence_blocks_missing_xcode_installation(
    tmp_path: Path,
) -> None:
    result = build_mobile_xcode_build_evidence_report(
        repo_root=tmp_path,
        returncode=127,
        stdout="",
        stderr=(
            "Xcode build gate could not find xcodebuild at "
            "/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild.\n"
        ),
    )

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["classification"] == "blocked_by_xcode_installation"
    assert result.report["checks"][0]["id"] == "xcode_installation"
    assert result.report["operator_actions"] == [
        "install Xcode or set DEVELOPER_DIR, then rerun make mobile-xcode-build-evidence"
    ]


def test_xcode_build_evidence_classifies_project_build_failure(
    tmp_path: Path,
) -> None:
    result = build_mobile_xcode_build_evidence_report(
        repo_root=tmp_path,
        returncode=65,
        stdout="CompileSwift failed\n** BUILD FAILED **\n",
        stderr="",
    )

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["classification"] == "xcode_project_build_failed"
    assert result.report["checks"][0]["id"] == "xcode_project_build"
    assert result.report["operator_actions"] == [
        "fix the iOS project build error, then rerun make mobile-xcode-build-evidence"
    ]


def test_run_xcode_build_evidence_uses_injected_runner(tmp_path: Path) -> None:
    calls: list[Path] = []

    def runner(repo_root: Path) -> subprocess.CompletedProcess[str]:
        calls.append(repo_root)
        return subprocess.CompletedProcess(
            args=["apps/mobile/ios/scripts/xcode_build_gate.sh"],
            returncode=0,
            stdout="** BUILD SUCCEEDED **\n",
            stderr="",
        )

    result = run_mobile_xcode_build_evidence(
        repo_root=tmp_path,
        command_runner=runner,
    )

    assert calls == [tmp_path]
    assert result.exit_code == 0
    assert result.report["status"] == "ready"


def test_cli_writes_mobile_xcode_build_evidence_blocked_report(
    tmp_path: Path,
) -> None:
    repo_root = _minimal_xcode_gate_repo(tmp_path)
    output = repo_root / "services/backend/.local/mobile-xcode-build-evidence.json"

    exit_code = main(
        [
            "mobile-xcode-build-evidence",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output),
        ]
    )
    report = json.loads(output.read_text(encoding="utf-8"))

    assert exit_code == 2
    assert report["kind"] == "mobile_xcode_build_evidence_report"
    assert report["status"] == "blocked"
    assert report["classification"] == "blocked_by_apple_sdk_license"
    assert "license" in " ".join(report["stderr_lines"]).lower()
    assert str(tmp_path) not in json.dumps(report)


def test_makefile_exposes_mobile_xcode_build_evidence_target() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    text = (repo_root / "Makefile").read_text(encoding="utf-8")
    wrapper = (
        repo_root / "services/backend/scripts/write_mobile_xcode_build_evidence.sh"
    ).read_text(encoding="utf-8")

    assert "mobile-xcode-build-evidence" in text
    assert "services/backend/scripts/write_mobile_xcode_build_evidence.sh" in text
    assert "myth_forge_api.cli mobile-xcode-build-evidence" in wrapper
    assert ".local/mobile-xcode-build-evidence.json" in wrapper


def _minimal_xcode_gate_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    script = repo_root / "apps/mobile/ios/scripts/xcode_build_gate.sh"
    (repo_root / "services/backend/.local").mkdir(parents=True)
    script.parent.mkdir(parents=True)
    script.write_text(
        "#!/usr/bin/env sh\n"
        "printf '%s\\n' 'You have not agreed to the Xcode license agreements.' >&2\n"
        "exit 69\n",
        encoding="utf-8",
    )
    return repo_root
