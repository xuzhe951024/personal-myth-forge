from __future__ import annotations

import json
import shutil
import struct
from pathlib import Path

from myth_forge_api.final_local_report_refresh import run_final_local_report_refresh
from myth_forge_api.visual_regression import DEFAULT_VISUAL_ARTIFACTS


def test_final_local_report_refresh_writes_safe_reports_without_live_or_global_actions(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = run_final_local_report_refresh(repo_root=repo_root)
    report_text = json.dumps(result.report)
    steps = {step["id"]: step for step in result.report["steps"]}
    final_acceptance = json.loads(
        (repo_root / "services/backend/.local/final-acceptance-local.json").read_text(
            encoding="utf-8"
        )
    )

    assert result.exit_code == 2
    assert result.report["kind"] == "final_local_report_refresh_report"
    assert result.report["status"] == "blocked"
    assert result.report["summary"]["failed"] == 0
    assert result.report["summary"]["blocked"] >= 1
    assert steps["final_acceptance_local"]["status"] == "blocked"
    assert steps["final_acceptance_local"]["accepted_blocked"] is True
    assert steps["final_resource_fill_guide"]["status"] == "blocked"
    assert steps["final_configured_evidence_plan"]["status"] == "blocked"
    assert steps["configured_live_evidence_bundle"]["status"] == "blocked"
    assert steps["configured_live_evidence_bundle"]["accepted_blocked"] is True
    assert steps["mobile_deploy_preflight_evidence"]["status"] == "blocked"
    assert steps["mobile_deploy_preflight_evidence"]["accepted_blocked"] is True
    assert steps["mobile_xcode_build_evidence"]["status"] == "blocked"
    assert steps["mobile_xcode_build_evidence"]["accepted_blocked"] is True
    assert final_acceptance["refresh_safety"] == {
        "mobile_gate_commands_executed": False,
        "xcode_or_signing_executed": False,
        "live_provider_calls": False,
        "detail": (
            "final-local-report-refresh records blocked device/Xcode gates without "
            "executing those commands"
        ),
    }
    assert steps["final_showcase_readiness"]["status"] == "blocked"
    assert steps["final_launch_closure_packet"]["status"] == "blocked"
    assert steps["final_launch_closure_packet"]["accepted_blocked"] is True
    assert result.report["safety"] == {
        "live_provider_calls": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "writes_repo_local_reports": True,
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
    }
    for relative_path in (
        "services/backend/.local/final-resource-requirements.json",
        "services/backend/.local/final-resource-repair-preview.json",
        "services/backend/.local/final-resource-apply-preview.json",
        "services/backend/.local/final-resource-fill-guide.json",
        "services/backend/.local/final-resource-fill-guide.md",
        "services/backend/.local/3d-evaluation-local.json",
        "services/backend/.local/npc-evaluation-local.json",
        "services/backend/.local/provider-handoff.json",
        "services/backend/.local/visual-regression-local.json",
        "services/backend/.local/final-acceptance-local.json",
        "services/backend/.local/final-demo-launch-local.json",
        "services/backend/.local/ios-deploy-runbook-local.json",
        "services/backend/.local/mobile-deploy-preflight-evidence.json",
        "services/backend/.local/mobile-xcode-build-evidence.json",
        "services/backend/.local/final-configured-preflight.json",
        "services/backend/.local/final-configured-evidence-plan.json",
        "services/backend/.local/final-handoff-index.json",
        "services/backend/.local/ios-device-launch-certificate.json",
        "services/backend/.local/ios-device-launch-rehearsal.json",
        "services/backend/.local/ios-device-evidence-bundle.json",
        "services/backend/.local/live-provider-evidence.json",
        "services/backend/.local/configured-live-evidence-bundle.json",
        "services/backend/.local/print-fulfillment-readiness.json",
        "services/backend/.local/final-external-action-ledger.json",
        "services/backend/.local/final-showcase-readiness.json",
        "services/backend/.local/final-launch-closure-packet.json",
    ):
        assert (repo_root / relative_path).exists(), relative_path
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "meshy-secret" not in report_text


def test_final_local_report_refresh_writes_safe_xcode_evidence_snapshot(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    xcode_path = repo_root / "services/backend/.local/mobile-xcode-build-evidence.json"

    result = run_final_local_report_refresh(repo_root=repo_root)
    steps = {step["id"]: step for step in result.report["steps"]}
    xcode_report = json.loads(xcode_path.read_text(encoding="utf-8"))

    assert result.exit_code == 2
    assert steps["mobile_xcode_build_evidence"]["status"] == "blocked"
    assert steps["mobile_xcode_build_evidence"]["accepted_blocked"] is True
    assert steps["mobile_xcode_build_evidence"]["output"] == (
        "services/backend/.local/mobile-xcode-build-evidence.json"
    )
    assert xcode_report["kind"] == "mobile_xcode_build_evidence_report"
    assert xcode_report["status"] == "blocked"
    assert xcode_report["classification"] == (
        "xcode_build_gate_not_run_by_final_local_report_refresh"
    )
    assert xcode_report["checks"][0]["id"] == "xcode_build_gate"
    assert xcode_report["checks"][0]["status"] == "blocked"
    assert xcode_report["operator_actions"] == [
        "run make mobile-xcode-build-evidence outside final-local-report-refresh"
    ]
    assert xcode_report["safety"]["commands_run"] is False
    assert xcode_report["safety"]["xcode_or_signing"] is False
    assert xcode_report["safety"]["global_mutation"] is False
    assert xcode_report["safety"]["writes_derived_data"] is False


def test_final_local_report_refresh_preserves_existing_mobile_deploy_preflight_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    evidence_path = (
        repo_root / "services/backend/.local/mobile-deploy-preflight-evidence.json"
    )
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        json.dumps(_ready_mobile_deploy_preflight_evidence(), indent=2),
        encoding="utf-8",
    )

    result = run_final_local_report_refresh(repo_root=repo_root)
    preserved = json.loads(evidence_path.read_text(encoding="utf-8"))
    steps = {step["id"]: step for step in result.report["steps"]}

    assert result.exit_code == 2
    assert steps["mobile_deploy_preflight_evidence"]["status"] == "ready"
    assert steps["mobile_deploy_preflight_evidence"]["accepted_blocked"] is False
    assert preserved["status"] == "ready"
    assert preserved["checks"][0]["id"] == "deploy_preflight"
    assert preserved["safety"]["commands_run"] is True


def test_final_local_report_refresh_preserves_existing_xcode_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    xcode_path = repo_root / "services/backend/.local/mobile-xcode-build-evidence.json"
    xcode_path.parent.mkdir(parents=True, exist_ok=True)
    xcode_path.write_text(
        json.dumps(
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
                    "accept the Xcode license outside Codex, "
                    "then rerun make mobile-xcode-build-evidence"
                ],
                "safety": {
                    "commands_run": True,
                    "xcode_or_signing": True,
                    "global_mutation": False,
                    "writes_derived_data": True,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_final_local_report_refresh(repo_root=repo_root)
    preserved = json.loads(xcode_path.read_text(encoding="utf-8"))

    assert result.exit_code == 2
    assert preserved["classification"] == "blocked_by_apple_sdk_license"
    assert preserved["checks"][0]["id"] == "xcode_license"
    assert preserved["safety"]["commands_run"] is True


def test_final_local_report_refresh_reuses_ready_device_gate_evidence_for_final_acceptance(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    local_dir = repo_root / "services/backend/.local"
    local_dir.mkdir(parents=True, exist_ok=True)
    (local_dir / "mobile-deploy-preflight-evidence.json").write_text(
        json.dumps(_ready_mobile_deploy_preflight_evidence(), indent=2),
        encoding="utf-8",
    )
    (local_dir / "mobile-xcode-build-evidence.json").write_text(
        json.dumps(_ready_mobile_xcode_build_evidence(), indent=2),
        encoding="utf-8",
    )

    result = run_final_local_report_refresh(repo_root=repo_root)
    final_acceptance = json.loads(
        (local_dir / "final-acceptance-local.json").read_text(encoding="utf-8")
    )
    checks = {check["id"]: check for check in final_acceptance["checks"]}

    assert result.exit_code == 2
    assert checks["mobile_deploy_preflight"]["status"] == "passed"
    assert checks["mobile_deploy_preflight"]["classification"] == "command_succeeded"
    assert checks["mobile_deploy_preflight"]["exit_code"] == 0
    assert "Backend health: ok" in checks["mobile_deploy_preflight"]["stdout_tail"]
    assert checks["mobile_xcode_build"]["status"] == "passed"
    assert checks["mobile_xcode_build"]["classification"] == "command_succeeded"
    assert checks["mobile_xcode_build"]["exit_code"] == 0
    assert final_acceptance["refresh_safety"]["mobile_gate_commands_executed"] is False
    assert final_acceptance["refresh_safety"]["xcode_or_signing_executed"] is False


def test_final_local_report_refresh_reports_unexpected_step_failure(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    def fail_step(_repo_root: Path) -> dict[str, object]:
        raise RuntimeError(f"unexpected file://{tmp_path}/secret.txt")

    result = run_final_local_report_refresh(
        repo_root=repo_root,
        extra_steps={"forced_failure": fail_step},
    )
    report_text = json.dumps(result.report)
    steps = {step["id"]: step for step in result.report["steps"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert steps["forced_failure"]["status"] == "failed"
    assert steps["forced_failure"]["exit_code"] == 1
    assert "unexpected" in steps["forced_failure"]["error"]
    assert "[redacted]" in steps["forced_failure"]["error"]
    assert "secret.txt" not in report_text
    assert "file://" not in report_text
    assert str(tmp_path) not in report_text
    assert result.report["safety"]["live_provider_calls"] is False
    assert result.report["safety"]["global_mutation"] is False
    assert result.report["safety"]["xcode_or_signing"] is False


def test_final_local_report_refresh_writes_final_showcase_after_rehearsal(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = run_final_local_report_refresh(repo_root=repo_root)
    steps = {step["id"]: index for index, step in enumerate(result.report["steps"])}
    showcase = json.loads(
        (repo_root / "services/backend/.local/final-showcase-readiness.json").read_text(
            encoding="utf-8"
        )
    )
    configured_bundle = json.loads(
        (
            repo_root / "services/backend/.local/configured-live-evidence-bundle.json"
        ).read_text(encoding="utf-8")
    )
    closure_packet = json.loads(
        (
            repo_root / "services/backend/.local/final-launch-closure-packet.json"
        ).read_text(encoding="utf-8")
    )

    assert result.exit_code == 2
    assert steps["ios_deploy_runbook_local"] < steps["mobile_deploy_preflight_evidence"]
    assert steps["mobile_deploy_preflight_evidence"] < steps["mobile_xcode_build_evidence"]
    assert steps["mobile_deploy_preflight_evidence"] < steps["ios_device_launch_rehearsal"]
    assert steps["mobile_xcode_build_evidence"] < steps["ios_device_evidence_bundle"]
    assert steps["npc_evaluation_local"] < steps["provider_handoff"]
    assert steps["provider_handoff"] < steps["final_acceptance_local"]
    assert steps["ios_device_launch_rehearsal"] < steps["ios_device_evidence_bundle"]
    assert steps["ios_device_evidence_bundle"] < steps["final_showcase_readiness"]
    assert steps["live_provider_evidence"] < steps["configured_live_evidence_bundle"]
    assert steps["configured_live_evidence_bundle"] < steps["final_showcase_readiness"]
    assert steps["ios_device_launch_rehearsal"] < steps["final_showcase_readiness"]
    assert steps["configured_live_evidence_bundle"] < steps["final_launch_closure_packet"]
    assert steps["print_fulfillment_readiness"] < steps["final_launch_closure_packet"]
    assert steps["final_external_action_ledger"] < steps["final_launch_closure_packet"]
    assert steps["final_showcase_readiness"] < steps["final_launch_closure_packet"]
    provider_handoff = json.loads(
        (repo_root / "services/backend/.local/provider-handoff.json").read_text(
            encoding="utf-8"
        )
    )
    assert provider_handoff["kind"] == "provider_handoff_report"
    assert provider_handoff["status"] == "blocked"
    assert provider_handoff["classification"] == "core_real_providers_not_ready"
    bundle = json.loads(
        (
            repo_root / "services/backend/.local/ios-device-evidence-bundle.json"
        ).read_text(encoding="utf-8")
    )
    assert bundle["kind"] == "ios_device_evidence_bundle_report"
    assert bundle["safety"]["commands_run"] is False
    assert bundle["safety"]["xcode_or_signing"] is False
    assert configured_bundle["kind"] == "configured_live_evidence_bundle_report"
    assert configured_bundle["safety"]["commands_run"] is False
    assert configured_bundle["safety"]["live_provider_calls"] is False
    assert showcase["evidence"]["ios_device_launch_rehearsal_readiness"]["kind"] == (
        "ios_device_launch_rehearsal_readiness_report"
    )
    assert showcase["evidence"]["configured_live_evidence_bundle"]["kind"] == (
        "configured_live_evidence_bundle_report"
    )
    assert showcase["evidence"]["configured_live_evidence_bundle"]["status"] == (
        configured_bundle["status"]
    )
    assert closure_packet["kind"] == "final_launch_closure_packet_report"
    assert closure_packet["sections_by_id"]["configured_evidence_bundle"][
        "first_action"
    ]["id"] == "configured_live_evidence_bundle"
    assert closure_packet["sections_by_id"]["configured_evidence_bundle"]["command"] == (
        "make configured-live-evidence-bundle"
    )
    assert closure_packet["source_reports"]["configured_live_evidence_bundle"][
        "status"
    ] == configured_bundle["status"]
    assert "make configured-live-evidence-bundle" in closure_packet["commands"]
    assert str(tmp_path) not in json.dumps(showcase)


def _repo_fixture(tmp_path: Path) -> Path:
    source_root = Path(__file__).resolve().parents[3]
    repo_root = tmp_path / "repo"
    for relative_path in ("apps", "docs", "packages"):
        shutil.copytree(
            source_root / relative_path,
            repo_root / relative_path,
            ignore=shutil.ignore_patterns(".build", "__pycache__", ".DS_Store"),
        )
    backend_root = repo_root / "services/backend"
    backend_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source_root / "services/backend/src",
        backend_root / "src",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(
        source_root / "services/backend/scripts",
        backend_root / "scripts",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(
        source_root / "services/backend/tests",
        backend_root / "tests",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    for relative_path in (
        ".gitignore",
        ".env.example",
        "Makefile",
        "README.md",
        "services/backend/final-resources.env.example",
    ):
        destination = repo_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_root / relative_path, destination)
    _write_visual_artifacts(repo_root)
    return repo_root


def _write_visual_artifacts(repo_root: Path) -> None:
    for spec in DEFAULT_VISUAL_ARTIFACTS:
        html_path = repo_root / spec.html_path
        png_path = repo_root / spec.png_path
        html_path.parent.mkdir(parents=True, exist_ok=True)
        png_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text("\n".join(spec.required_text), encoding="utf-8")
        png_path.write_bytes(_png_header(spec.width, spec.height))
        if spec.notes_path:
            notes_path = repo_root / spec.notes_path
            notes_path.parent.mkdir(parents=True, exist_ok=True)
            notes_path.write_text("visual regression fixture", encoding="utf-8")


def _ready_mobile_deploy_preflight_evidence() -> dict[str, object]:
    return {
        "kind": "mobile_deploy_preflight_evidence_report",
        "status": "ready",
        "command": "make mobile-deploy-preflight",
        "script": "apps/mobile/ios/scripts/deploy_preflight.sh",
        "exit_code": 0,
        "checks": [
            {
                "id": "deploy_preflight",
                "label": "iOS deploy preflight",
                "status": "ready",
                "detail": "iOS deploy preflight passed.",
            },
            {
                "id": "backend_health",
                "label": "Backend health",
                "status": "ready",
                "detail": "Backend health: ok",
            },
            {
                "id": "final_launch_mode",
                "label": "Final launch mode",
                "status": "ready",
                "detail": "Final launch mode: local",
            },
        ],
        "stdout_lines": [
            "iOS deploy preflight passed.",
            "Backend health: ok",
            "Final launch mode: local",
        ],
        "stderr_lines": [],
        "operator_actions": [],
        "safety": {
            "commands_run": True,
            "provider_calls": False,
            "live_provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "global_mutation": False,
            "xcode_or_signing": False,
            "keychain_writes": False,
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
        },
    }


def _ready_mobile_xcode_build_evidence() -> dict[str, object]:
    return {
        "kind": "mobile_xcode_build_evidence_report",
        "status": "ready",
        "classification": "ready",
        "command": "make mobile-xcode-build",
        "script": "apps/mobile/ios/scripts/xcode_build_gate.sh",
        "exit_code": 0,
        "checks": [
            {
                "id": "xcode_build_gate",
                "label": "Xcode build gate",
                "status": "ready",
                "detail": "Xcode build gate passed with code signing disabled.",
            }
        ],
        "stdout_lines": ["Xcode build gate passed with code signing disabled."],
        "stderr_lines": [],
        "operator_actions": [],
        "safety": {
            "commands_run": True,
            "provider_calls": False,
            "live_provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "global_mutation": False,
            "xcode_or_signing": True,
            "code_signing_allowed": False,
            "keychain_writes": False,
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "writes_derived_data": True,
            "derived_data_path": "apps/mobile/ios/.build/xcode-derived-data",
        },
    }


def _png_header(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
        + b"\x00\x00\x00\x00"
    )
