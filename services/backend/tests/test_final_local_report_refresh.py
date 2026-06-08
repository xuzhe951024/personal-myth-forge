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
    ):
        assert (repo_root / relative_path).exists(), relative_path
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "meshy-secret" not in report_text


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

    assert result.exit_code == 2
    assert steps["ios_deploy_runbook_local"] < steps["mobile_deploy_preflight_evidence"]
    assert steps["mobile_deploy_preflight_evidence"] < steps["ios_device_launch_rehearsal"]
    assert steps["npc_evaluation_local"] < steps["provider_handoff"]
    assert steps["provider_handoff"] < steps["final_acceptance_local"]
    assert steps["ios_device_launch_rehearsal"] < steps["ios_device_evidence_bundle"]
    assert steps["ios_device_evidence_bundle"] < steps["final_showcase_readiness"]
    assert steps["live_provider_evidence"] < steps["configured_live_evidence_bundle"]
    assert steps["configured_live_evidence_bundle"] < steps["final_showcase_readiness"]
    assert steps["ios_device_launch_rehearsal"] < steps["final_showcase_readiness"]
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


def _png_header(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
        + b"\x00\x00\x00\x00"
    )
