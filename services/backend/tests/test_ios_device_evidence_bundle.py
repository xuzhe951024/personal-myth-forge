from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api.cli import main
from myth_forge_api.ios_device_evidence_bundle import (
    build_ios_device_evidence_bundle_report,
)


def test_ios_device_evidence_bundle_blocks_missing_local_device_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = build_ios_device_evidence_bundle_report(repo_root=repo_root)

    assert result.exit_code == 2
    assert result.report["kind"] == "ios_device_evidence_bundle_report"
    assert result.report["status"] == "blocked"
    assert result.report["summary"]["required"] == 4
    assert result.report["summary"]["global_actions"] == 1
    slots = {slot["id"]: slot for slot in result.report["evidence_slots"]}
    first_blocker = result.report["first_blocker"]
    next_action = result.report["next_action"]
    assert list(slots) == [
        "backend_device_server",
        "mobile_deploy_preflight",
        "xcode_build_gate",
        "ios_device_launch_rehearsal",
    ]
    assert slots["backend_device_server"]["command"] == "make backend-device-demo"
    assert slots["mobile_deploy_preflight"]["command"] == "make mobile-deploy-preflight"
    assert slots["xcode_build_gate"]["command"] == "make mobile-xcode-build"
    assert slots["xcode_build_gate"]["global_action"] is True
    assert slots["xcode_build_gate"]["xcode_or_signing"] is True
    assert (
        slots["ios_device_launch_rehearsal"]["command"]
        == "make ios-device-launch-rehearsal"
    )
    assert first_blocker["id"] == "backend_device_server"
    assert first_blocker["command"] == "make backend-device-demo"
    assert next_action == {**first_blocker, "source": "first_blocker"}
    actions = " ".join(result.report["operator_actions"])
    assert "make backend-device-demo" in actions
    assert "make mobile-deploy-preflight" in actions
    assert "make ios-device-launch-rehearsal" in actions
    assert (
        "make ios-device-launch-rehearsal | "
        "Run iOS device launch rehearsal to refresh final device evidence."
        in result.report["operator_actions"]
    )
    assert "run make ios-device-launch-rehearsal" not in actions
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["xcode_or_signing"] is False
    assert result.report["safety"]["describes_global_actions"] is True


def test_ios_device_evidence_bundle_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = build_ios_device_evidence_bundle_report(repo_root=repo_root)
    bundle = result.report["device_action_bundle"]

    assert bundle["id"] == "ios_device_evidence_actions"
    assert bundle["status"] == "blocked"
    assert bundle["first_action"]["id"] == "backend_device_server"
    assert bundle["first_action"]["command"] == "make backend-device-demo"
    assert bundle["first_action"]["next_action"]["command"] == "make backend-device-demo"
    assert bundle["summary"] == {
        "actions": 4,
        "ready": 0,
        "missing": 4,
        "blocked": 0,
        "manual": 4,
        "provider_calls": 0,
        "global_actions": 1,
        "xcode_or_signing": 1,
    }
    assert bundle["safety"] == {
        "commands_run": False,
        "global_mutation": False,
        "keychain_writes": False,
        "live_provider_calls": False,
        "provider_calls": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "xcode_or_signing": False,
    }
    assert "sk-" not in json.dumps(bundle)
    assert str(tmp_path) not in json.dumps(bundle)


def test_ios_device_evidence_bundle_normalizes_stale_launch_rehearsal_detail(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_ios_device_launch_rehearsal(
        repo_root,
        {
            "kind": "ios_device_launch_rehearsal_report",
            "status": "blocked",
            "operator_actions": [
                (
                    "rerun make ios-device-launch-rehearsal to regenerate "
                    "services/backend/.local/ios-device-launch-rehearsal.json "
                    "for the current product sources"
                )
            ],
        },
    )

    result = build_ios_device_evidence_bundle_report(repo_root=repo_root)
    actions = " ".join(result.report["operator_actions"])

    assert (
        "make ios-device-launch-rehearsal | "
        "Run iOS device launch rehearsal to refresh final device evidence."
        in result.report["operator_actions"]
    )
    assert "run make ios-device-launch-rehearsal" not in actions
    assert "rerun make ios-device-launch-rehearsal" not in actions


def test_ios_device_evidence_bundle_marks_ready_saved_device_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_final_acceptance(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "passed",
                    "classification": "passed",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stdout_tail": "iOS deploy preflight passed. Backend health: ok",
                },
                {
                    "id": "mobile_xcode_build",
                    "label": "Xcode build gate",
                    "status": "passed",
                    "classification": "passed",
                    "command": ["make", "mobile-xcode-build"],
                    "stdout_tail": "Build succeeded.",
                },
            ],
        },
    )
    _write_ios_device_launch_rehearsal(
        repo_root,
        {
            "kind": "ios_device_launch_rehearsal_report",
            "status": "ready",
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
                    "id": "final_rehearsal_local",
                    "label": "Local final rehearsal",
                    "status": "ready",
                    "command": "make final-rehearsal-local",
                    "classification": "saved_report_set",
                }
            ],
            "operator_actions": ["iOS device launch rehearsal is ready"],
            "commands": ["make ios-device-launch-rehearsal"],
            "safety": {
                "commands_run": False,
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

    result = build_ios_device_evidence_bundle_report(repo_root=repo_root)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["summary"]["ready"] == 4
    assert result.report["summary"]["blocked"] == 0
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
    assert result.report["operator_actions"] == ["iOS device evidence is ready"]
    assert all(slot["status"] == "ready" for slot in result.report["evidence_slots"])
    bundle = result.report["device_action_bundle"]

    assert bundle["status"] == "ready"
    assert bundle["first_action"] is None
    assert bundle["summary"]["ready"] == 4
    assert bundle["summary"]["blocked"] == 0
    assert all(action["status"] == "ready" for action in bundle["actions"])


def test_ios_device_evidence_bundle_redacts_unsafe_saved_details(tmp_path: Path) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_final_acceptance(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 2, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_backend_health",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stderr_tail": (
                        "Authorization=Bearer sk-secret /Users/zhexu/private "
                        "file:///tmp/private checkout_url=https://pay.example"
                    ),
                }
            ],
        },
    )

    result = build_ios_device_evidence_bundle_report(repo_root=repo_root)
    text = json.dumps(result.report)

    assert result.exit_code == 2
    assert "[redacted]" in text
    assert "sk-secret" not in text
    assert "/Users/" not in text
    assert "file:///" not in text
    assert "checkout_url" not in text


def test_ios_device_evidence_bundle_uses_saved_xcode_evidence(tmp_path: Path) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_final_acceptance(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 2, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_backend_health",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stderr_tail": "Backend health check failed.",
                },
                {
                    "id": "mobile_xcode_build",
                    "label": "Xcode build gate",
                    "status": "blocked",
                    "classification": "command_failed",
                    "command": ["make", "mobile-xcode-build"],
                    "stderr_tail": "generic Xcode failure",
                },
            ],
        },
    )
    _write_mobile_xcode_build_evidence(
        repo_root,
        {
            "kind": "mobile_xcode_build_evidence_report",
            "status": "blocked",
            "classification": "blocked_by_apple_sdk_license",
            "checks": [
                {
                    "id": "xcode_license",
                    "label": "Xcode license",
                    "status": "blocked",
                    "detail": "Apple SDK license agreement is not accepted.",
                }
            ],
            "operator_actions": [
                "accept the Xcode license outside Codex, then rerun make mobile-xcode-build-evidence"
            ],
        },
    )

    result = build_ios_device_evidence_bundle_report(repo_root=repo_root)
    slots = {slot["id"]: slot for slot in result.report["evidence_slots"]}

    assert result.exit_code == 2
    assert slots["xcode_build_gate"]["status"] == "blocked"
    assert slots["xcode_build_gate"]["classification"] == "blocked_by_apple_sdk_license"
    assert (
        slots["xcode_build_gate"]["detail"]
        == "Apple SDK license agreement is not accepted."
    )
    assert (
        slots["xcode_build_gate"]["evidence_source"]
        == "services/backend/.local/mobile-xcode-build-evidence.json"
    )
    assert "mobile_xcode_build_evidence" in result.report["source_reports"]


def test_ios_device_evidence_bundle_uses_saved_mobile_preflight_evidence_details(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_final_acceptance(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_backend_health",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stderr_tail": (
                        "start backend-device-demo and rerun mobile deploy preflight"
                    ),
                }
            ],
        },
    )
    _write_mobile_deploy_preflight_evidence(
        repo_root,
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "blocked",
            "command": "make mobile-deploy-preflight",
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
            "operator_actions": [
                "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL",
            ],
        },
    )

    result = build_ios_device_evidence_bundle_report(repo_root=repo_root)
    slots = {slot["id"]: slot for slot in result.report["evidence_slots"]}
    text = json.dumps(result.report)

    assert result.exit_code == 2
    assert slots["backend_device_server"]["detail"] == (
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    assert slots["backend_device_server"]["evidence_source"] == (
        "services/backend/.local/mobile-deploy-preflight-evidence.json"
    )
    assert slots["mobile_deploy_preflight"]["detail"] == (
        "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    assert slots["mobile_deploy_preflight"]["evidence_source"] == (
        "services/backend/.local/mobile-deploy-preflight-evidence.json"
    )
    assert "mobile_deploy_preflight_evidence" in result.report["source_reports"]
    assert "MESHY_API_KEY" not in text


def test_ios_device_evidence_bundle_source_reports_preserve_mobile_device_action_bundles(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_mobile_deploy_preflight_evidence(
        repo_root,
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "blocked",
            "summary": {"blocked": 2},
            "device_action_bundle": {
                "id": "mobile_deploy_preflight_evidence_actions",
                "label": "Mobile Deploy Preflight Evidence Actions",
                "source_report": "mobile_deploy_preflight_evidence",
                "status": "blocked",
                "actions": [
                    {
                        "id": "development_team",
                        "label": "Apple Team ID",
                        "status": "blocked",
                        "classification": "",
                        "command": (
                            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                            "make mobile-write-deploy-config-auto"
                        ),
                        "detail": "Missing DEVELOPMENT_TEAM sk-test",
                        "manual": True,
                        "provider_calls": False,
                        "global_action": False,
                        "xcode_or_signing": False,
                    }
                ],
                "first_action": {
                    "id": "development_team",
                    "label": "Apple Team ID",
                    "status": "blocked",
                    "command": (
                        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                        "make mobile-write-deploy-config-auto"
                    ),
                    "validation_command": "make mobile-deploy-preflight",
                },
                "summary": {
                    "actions": 1,
                    "ready": 0,
                    "missing": 0,
                    "blocked": 1,
                    "manual": 1,
                    "provider_calls": 0,
                    "global_actions": 0,
                    "xcode_or_signing": 0,
                },
                "safety": {
                    "commands_run": True,
                    "xcode_or_signing": False,
                    "provider_calls": False,
                },
            },
        },
    )
    _write_mobile_xcode_build_evidence(
        repo_root,
        {
            "kind": "mobile_xcode_build_evidence_report",
            "status": "blocked",
            "classification": "blocked_by_apple_sdk_license",
            "summary": {"blocked": 1},
            "device_action_bundle": {
                "id": "mobile_xcode_build_evidence_actions",
                "label": "Mobile Xcode Build Evidence Actions",
                "source_report": "mobile_xcode_build_evidence",
                "status": "blocked",
                "actions": [
                    {
                        "id": "xcode_license",
                        "label": "Xcode license",
                        "status": "blocked",
                        "classification": "blocked_by_apple_sdk_license",
                        "command": (
                            "accept the Xcode license outside Codex, then rerun "
                            "make mobile-xcode-build-evidence"
                        ),
                        "detail": f"Apple SDK license at {repo_root}",
                        "manual": True,
                        "provider_calls": False,
                        "global_action": True,
                        "xcode_or_signing": True,
                    }
                ],
                "first_action": {
                    "id": "xcode_license",
                    "label": "Xcode license",
                    "status": "blocked",
                    "command": (
                        "accept the Xcode license outside Codex, then rerun "
                        "make mobile-xcode-build-evidence"
                    ),
                    "validation_command": "make mobile-xcode-build-evidence",
                },
                "summary": {
                    "actions": 1,
                    "ready": 0,
                    "missing": 0,
                    "blocked": 1,
                    "manual": 1,
                    "provider_calls": 0,
                    "global_actions": 1,
                    "xcode_or_signing": 1,
                },
                "safety": {
                    "commands_run": True,
                    "xcode_or_signing": True,
                    "code_signing_allowed": False,
                },
            },
        },
    )

    result = build_ios_device_evidence_bundle_report(repo_root=repo_root)
    sources = result.report["source_reports"]
    report_text = json.dumps(result.report)
    deploy_bundle = sources["mobile_deploy_preflight_evidence"]["device_action_bundle"]
    xcode_bundle = sources["mobile_xcode_build_evidence"]["device_action_bundle"]

    assert deploy_bundle["id"] == "mobile_deploy_preflight_evidence_actions"
    assert deploy_bundle["first_action"]["id"] == "development_team"
    assert deploy_bundle["first_action"]["command"] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto"
    )
    assert deploy_bundle["safety"]["commands_run"] is True
    assert deploy_bundle["safety"]["xcode_or_signing"] is False
    assert xcode_bundle["id"] == "mobile_xcode_build_evidence_actions"
    assert xcode_bundle["first_action"]["id"] == "xcode_license"
    assert xcode_bundle["safety"]["xcode_or_signing"] is True
    assert xcode_bundle["safety"]["code_signing_allowed"] is False
    assert "sk-test" not in report_text
    assert str(repo_root) not in report_text


def test_ios_device_evidence_bundle_operator_actions_include_slot_details(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_final_acceptance(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 2, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_backend_health",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stderr_tail": (
                        "start backend-device-demo and rerun mobile deploy preflight"
                    ),
                },
                {
                    "id": "mobile_xcode_build",
                    "label": "Xcode build gate",
                    "status": "blocked",
                    "classification": "command_failed",
                    "command": ["make", "mobile-xcode-build"],
                    "stderr_tail": "generic Xcode failure",
                },
            ],
        },
    )
    _write_mobile_deploy_preflight_evidence(
        repo_root,
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "blocked",
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
        },
    )
    _write_mobile_xcode_build_evidence(
        repo_root,
        {
            "kind": "mobile_xcode_build_evidence_report",
            "status": "blocked",
            "classification": "blocked_by_apple_sdk_license",
            "checks": [
                {
                    "id": "xcode_license",
                    "label": "Xcode license",
                    "status": "blocked",
                    "detail": "Apple SDK license agreement is not accepted.",
                }
            ],
        },
    )
    _write_ios_device_launch_rehearsal(
        repo_root,
        {
            "kind": "ios_device_launch_rehearsal_report",
            "status": "blocked",
            "first_blocker": {
                "id": "final_rehearsal_local",
                "label": "Local final rehearsal",
                "status": "blocked",
                "classification": "step_blocked",
                "command": "make final-rehearsal-local",
                "detail": (
                    "final_rehearsal_local: mobile_deploy_preflight_evidence: "
                    "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be "
                    "iPhone-reachable"
                ),
            },
            "operator_actions": [
                (
                    "final_rehearsal_local: mobile_deploy_preflight_evidence: "
                    "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be "
                    "iPhone-reachable"
                )
            ],
        },
    )

    result = build_ios_device_evidence_bundle_report(repo_root=repo_root)
    actions = result.report["operator_actions"]
    slots = {slot["id"]: slot for slot in result.report["evidence_slots"]}
    text = json.dumps(result.report)

    assert result.exit_code == 2
    assert actions[0] == (
        "start backend-device-demo before device checks: make backend-device-demo; "
        "rerun make mobile-deploy-preflight | PMF_BACKEND_BASE_URL must be "
        "iPhone-reachable"
    )
    assert actions[1] == (
        "start backend-device-demo before device checks: make backend-device-demo; "
        "rerun make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    assert actions[2] == (
        "run Xcode build gate manually on the Mac: make mobile-xcode-build | "
        "Apple SDK license agreement is not accepted."
    )
    assert actions[3] == (
        "make ios-device-launch-rehearsal | "
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    assert not any(
        action.startswith("run make ios-device-launch-rehearsal")
        for action in actions
    )
    assert slots["ios_device_launch_rehearsal"]["detail"].startswith(
        "final_rehearsal_local: mobile_deploy_preflight_evidence:"
    )
    assert not any(
        " | final_rehearsal_local:" in action
        or " | mobile_deploy_preflight_evidence:" in action
        for action in actions
    )
    assert "MESHY_API_KEY" not in text


def test_cli_writes_ios_device_evidence_bundle_report(tmp_path: Path) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_mobile_xcode_build_evidence(
        repo_root,
        {
            "kind": "mobile_xcode_build_evidence_report",
            "status": "blocked",
            "classification": "blocked_by_apple_sdk_license",
            "checks": [
                {
                    "id": "xcode_license",
                    "label": "Xcode license",
                    "status": "blocked",
                    "detail": "Apple SDK license agreement is not accepted.",
                }
            ],
            "operator_actions": [
                "accept the Xcode license outside Codex, then rerun make mobile-xcode-build-evidence"
            ],
        },
    )
    output = repo_root / "services/backend/.local/ios-device-evidence-bundle.json"

    exit_code = main(
        [
            "ios-device-evidence-bundle",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output),
        ]
    )
    report = json.loads(output.read_text(encoding="utf-8"))
    slots = {slot["id"]: slot for slot in report["evidence_slots"]}

    assert exit_code == 2
    assert report["kind"] == "ios_device_evidence_bundle_report"
    assert slots["xcode_build_gate"]["classification"] == (
        "blocked_by_apple_sdk_license"
    )
    assert report["safety"]["commands_run"] is False
    assert report["safety"]["xcode_or_signing"] is False


def test_makefile_exposes_ios_device_evidence_bundle_target() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    text = (repo_root / "Makefile").read_text(encoding="utf-8")
    wrapper = (
        repo_root / "services/backend/scripts/write_ios_device_evidence_bundle.sh"
    ).read_text(encoding="utf-8")

    assert "ios-device-evidence-bundle" in text
    assert "services/backend/scripts/write_ios_device_evidence_bundle.sh" in text
    assert "myth_forge_api.cli ios-device-evidence-bundle" in wrapper
    assert ".local/ios-device-evidence-bundle.json" in wrapper


def _repo_fixture(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    (repo_root / "apps/mobile/ios/Config").mkdir(parents=True)
    (repo_root / "services/backend/.local").mkdir(parents=True)
    (repo_root / "apps/mobile/ios/Config/Deployment.xcconfig").write_text(
        "PMF_FINAL_LAUNCH_MODE = local\n",
        encoding="utf-8",
    )
    return repo_root


def _write_final_acceptance(repo_root: Path, payload: dict[str, object]) -> None:
    path = repo_root / "services/backend/.local/final-acceptance-local.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_ios_device_launch_rehearsal(
    repo_root: Path,
    payload: dict[str, object],
) -> None:
    path = repo_root / "services/backend/.local/ios-device-launch-rehearsal.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_mobile_xcode_build_evidence(
    repo_root: Path,
    payload: dict[str, object],
) -> None:
    path = repo_root / "services/backend/.local/mobile-xcode-build-evidence.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_mobile_deploy_preflight_evidence(
    repo_root: Path,
    payload: dict[str, object],
) -> None:
    path = repo_root / "services/backend/.local/mobile-deploy-preflight-evidence.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
