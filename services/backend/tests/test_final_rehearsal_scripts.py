from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


PROVIDER_HANDOFF_SAFE_WRAPPERS = [
    (
        "provider-handoff",
        "write_provider_handoff.sh",
        "accepted provider handoff exit code 2",
        "services/backend/.local/provider-handoff.json",
    ),
    (
        "resource-handoff",
        "write_resource_handoff.sh",
        "accepted resource handoff exit code 2",
        "services/backend/.local/resource-handoff.json",
    ),
    (
        "final-resources-preflight",
        "write_final_resources_preflight.sh",
        "accepted final resources preflight exit code 2",
        "services/backend/.local/final-resources-preflight.json",
    ),
    (
        "final-resource-requirements",
        "write_final_resource_requirements.sh",
        "accepted final resource requirements exit code 2",
        "services/backend/.local/final-resource-requirements.json",
    ),
    (
        "final-resource-apply-preview",
        "write_final_resource_apply_preview.sh",
        "accepted final resource apply preview exit code 2",
        "services/backend/.local/final-resource-apply-preview.json",
    ),
    (
        "final-configured-preflight",
        "write_final_configured_preflight.sh",
        "accepted final configured preflight exit code 2",
        "services/backend/.local/final-configured-preflight.json",
    ),
    (
        "final-configured-evidence-plan",
        "write_final_configured_evidence_plan.sh",
        "accepted final configured evidence plan exit code 2",
        "services/backend/.local/final-configured-evidence-plan.json",
    ),
    (
        "configured-live-evidence-bundle",
        "write_configured_live_evidence_bundle.sh",
        "accepted configured live evidence bundle exit code 2",
        "services/backend/.local/configured-live-evidence-bundle.json",
    ),
    (
        "live-provider-evidence",
        "write_live_provider_evidence.sh",
        "accepted live provider evidence exit code 2",
        "services/backend/.local/live-provider-evidence.json",
    ),
    (
        "print-fulfillment-readiness",
        "write_print_fulfillment_readiness.sh",
        "accepted print fulfillment readiness exit code 2",
        "services/backend/.local/print-fulfillment-readiness.json",
    ),
]


def test_write_final_acceptance_local_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_final_acceptance_local.sh")

    assert result.returncode == 0
    assert "accepted final acceptance exit code 2" in result.stdout
    assert "services/backend/.local/final-acceptance-local.json" in result.stdout


def test_write_final_acceptance_local_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_final_acceptance_local.sh")

    assert result.returncode == 1
    assert "failed before writing a usable report: exit 1" in result.stderr


def test_write_final_acceptance_configured_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_final_acceptance_configured.sh")

    assert result.returncode == 0
    assert "accepted configured final acceptance exit code 2" in result.stdout
    assert "services/backend/.local/final-acceptance-configured.json" in result.stdout
    fake_uv_args = (
        script_repo / "services/backend/.local/fake-uv-args.txt"
    ).read_text(encoding="utf-8")
    assert "final-acceptance" in fake_uv_args
    assert "--profile quick" in fake_uv_args
    assert "--provider-mode configured" in fake_uv_args
    assert "--require-real-core" in fake_uv_args
    assert "--allow-live-provider-calls" in fake_uv_args
    assert "--repo-root ../.." in fake_uv_args
    assert "--output .local/final-acceptance-configured.json" in fake_uv_args


def test_write_final_acceptance_configured_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_final_acceptance_configured.sh")

    assert result.returncode == 1
    assert (
        "configured final acceptance failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_ios_deploy_runbook_local_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_ios_deploy_runbook_local.sh")

    assert result.returncode == 0
    assert "accepted iOS deploy runbook exit code 2" in result.stdout
    assert "services/backend/.local/ios-deploy-runbook-local.json" in result.stdout


def test_write_ios_deploy_runbook_local_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_ios_deploy_runbook_local.sh")

    assert result.returncode == 1
    assert "failed before writing a usable report: exit 1" in result.stderr


def test_write_final_local_report_refresh_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_final_local_report_refresh.sh")

    assert result.returncode == 0
    assert "accepted final local report refresh exit code 2" in result.stdout
    assert "services/backend/.local/final-local-report-refresh.json" in result.stdout
    fake_uv_args = (
        script_repo / "services/backend/.local/fake-uv-args.txt"
    ).read_text(encoding="utf-8")
    assert "final-local-report-refresh" in fake_uv_args
    assert "--repo-root ../.." in fake_uv_args
    assert "--output .local/final-local-report-refresh.json" in fake_uv_args


def test_write_final_local_report_refresh_syncs_final_demo_launch(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_final_local_report_refresh.sh")
    fake_uv_args = (
        script_repo / "services/backend/.local/fake-uv-args.txt"
    ).read_text(encoding="utf-8")

    assert result.returncode == 0
    assert "wrote services/backend/.local/final-local-report-refresh.json" in result.stdout
    assert "wrote services/backend/.local/final-demo-launch-local.json" in result.stdout
    refresh_index = fake_uv_args.index("final-local-report-refresh")
    launch_index = fake_uv_args.index("final-demo-launch --mode local")
    assert refresh_index < launch_index
    assert "--output .local/final-local-report-refresh.json" in fake_uv_args
    assert "--output .local/final-demo-launch-local.json" in fake_uv_args


def test_write_final_local_report_refresh_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_final_local_report_refresh.sh")

    assert result.returncode == 1
    assert (
        "final local report refresh failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_mobile_deploy_preflight_evidence_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_mobile_deploy_preflight_evidence.sh")

    assert result.returncode == 0
    assert "accepted mobile deploy preflight evidence exit code 2" in result.stdout
    assert (
        "services/backend/.local/mobile-deploy-preflight-evidence.json"
        in result.stdout
    )


def test_write_mobile_deploy_preflight_evidence_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_mobile_deploy_preflight_evidence.sh")

    assert result.returncode == 1
    assert (
        "mobile deploy preflight evidence failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_final_showcase_readiness_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_final_showcase_readiness.sh")

    assert result.returncode == 0
    assert "accepted final showcase readiness exit code 2" in result.stdout
    assert "services/backend/.local/final-showcase-readiness.json" in result.stdout


def test_write_final_showcase_readiness_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_final_showcase_readiness.sh")

    assert result.returncode == 1
    assert (
        "final showcase readiness failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_mobile_xcode_build_evidence_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_mobile_xcode_build_evidence.sh")

    assert result.returncode == 0
    assert "accepted mobile Xcode build evidence exit code 2" in result.stdout
    assert "services/backend/.local/mobile-xcode-build-evidence.json" in result.stdout


def test_write_mobile_xcode_build_evidence_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_mobile_xcode_build_evidence.sh")

    assert result.returncode == 1
    assert (
        "mobile Xcode build evidence failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_ios_device_evidence_bundle_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_ios_device_evidence_bundle.sh")

    assert result.returncode == 0
    assert "accepted iOS device evidence bundle exit code 2" in result.stdout
    assert "services/backend/.local/ios-device-evidence-bundle.json" in result.stdout


def test_write_ios_device_evidence_bundle_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_ios_device_evidence_bundle.sh")

    assert result.returncode == 1
    assert (
        "iOS device evidence bundle failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_ios_device_launch_certificate_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_ios_device_launch_certificate.sh")

    assert result.returncode == 0
    assert "accepted iOS device launch certificate exit code 2" in result.stdout
    assert "services/backend/.local/ios-device-launch-certificate.json" in result.stdout


def test_write_ios_device_launch_certificate_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_ios_device_launch_certificate.sh")

    assert result.returncode == 1
    assert (
        "iOS device launch certificate failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_final_handoff_index_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_final_handoff_index.sh")

    assert result.returncode == 0
    assert "accepted final handoff index exit code 2" in result.stdout
    assert "services/backend/.local/final-handoff-index.json" in result.stdout


def test_write_final_handoff_index_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_final_handoff_index.sh")

    assert result.returncode == 1
    assert (
        "final handoff index failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_final_external_action_ledger_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_final_external_action_ledger.sh")

    assert result.returncode == 0
    assert "accepted final external action ledger exit code 2" in result.stdout
    assert "services/backend/.local/final-external-action-ledger.json" in result.stdout


def test_write_final_external_action_ledger_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_final_external_action_ledger.sh")

    assert result.returncode == 1
    assert (
        "final external action ledger failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_final_launch_closure_packet_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_final_launch_closure_packet.sh")

    assert result.returncode == 0
    assert "accepted final launch closure packet exit code 2" in result.stdout
    assert "services/backend/.local/final-launch-closure-packet.json" in result.stdout


def test_write_final_launch_closure_packet_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, "write_final_launch_closure_packet.sh")

    assert result.returncode == 1
    assert (
        "final launch closure packet failed before writing a usable report: exit 1"
        in result.stderr
    )


def test_write_ios_device_launch_rehearsal_accepts_blocked_report_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_make(script_repo, exit_code=2)
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, "write_ios_device_launch_rehearsal.sh")

    assert result.returncode == 0
    assert "accepted final rehearsal exit code 2" in result.stdout
    assert "accepted configured preflight exit code 2" in result.stdout
    assert "accepted final handoff index exit code 2" in result.stdout
    assert "accepted iOS device launch certificate exit code 2" in result.stdout
    assert "accepted iOS device launch rehearsal exit code 2" in result.stdout
    assert "accepted iOS device launch rehearsal readiness exit code 2" in result.stdout
    assert "accepted final launch rehearsal sync exit code 2" in result.stdout
    assert "services/backend/.local/ios-device-launch-rehearsal.json" in result.stdout
    assert (
        "services/backend/.local/ios-device-launch-rehearsal-readiness.json"
        in result.stdout
    )
    assert "services/backend/.local/final-demo-launch-local.json" in result.stdout
    fake_make_args = (
        script_repo / "services/backend/.local/fake-make-args.txt"
    ).read_text(encoding="utf-8")
    fake_uv_args = (
        script_repo / "services/backend/.local/fake-uv-args.txt"
    ).read_text(encoding="utf-8")
    assert "final-rehearsal-local" in fake_make_args
    assert "final-configured-preflight" in fake_uv_args
    assert "final-handoff-index" in fake_uv_args
    assert "ios-device-launch-certificate" in fake_uv_args
    assert "ios-device-launch-rehearsal" in fake_uv_args
    assert "ios-device-launch-rehearsal-readiness" in fake_uv_args
    assert "final-demo-launch --mode local" in fake_uv_args
    fake_uv_lines = fake_uv_args.splitlines()
    rehearsal_line_index = next(
        index
        for index, line in enumerate(fake_uv_lines)
        if "--output .local/ios-device-launch-rehearsal.json" in line
    )
    readiness_line_index = next(
        index
        for index, line in enumerate(fake_uv_lines)
        if "--output .local/ios-device-launch-rehearsal-readiness.json" in line
    )
    final_launch_line_index = next(
        index
        for index, line in enumerate(fake_uv_lines)
        if "final-demo-launch --mode local" in line
    )
    assert rehearsal_line_index < readiness_line_index < final_launch_line_index
    assert fake_uv_args.rfind("ios-device-launch-rehearsal") < fake_uv_args.rfind(
        "final-demo-launch --mode local"
    )


def test_write_ios_device_launch_rehearsal_syncs_final_launch_after_rehearsal(
    script_repo: Path,
) -> None:
    _write_fake_make(script_repo, exit_code=0)
    _write_fake_uv(script_repo, exit_code=0)

    result = _run_script(script_repo, "write_ios_device_launch_rehearsal.sh")
    fake_uv_args = (
        script_repo / "services/backend/.local/fake-uv-args.txt"
    ).read_text(encoding="utf-8")

    assert result.returncode == 0
    assert fake_uv_args.rfind("ios-device-launch-rehearsal") < fake_uv_args.rfind(
        "final-demo-launch --mode local"
    )
    assert fake_uv_args.rfind("ios-device-launch-rehearsal-readiness") < (
        fake_uv_args.rfind("final-demo-launch --mode local")
    )
    assert "--output .local/ios-device-launch-rehearsal-readiness.json" in fake_uv_args
    assert "--output .local/final-demo-launch-local.json" in fake_uv_args


def test_write_ios_device_launch_rehearsal_readiness_syncs_final_launch(
    script_repo: Path,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(
        script_repo,
        "write_ios_device_launch_rehearsal_readiness.sh",
    )
    fake_uv_args = (
        script_repo / "services/backend/.local/fake-uv-args.txt"
    ).read_text(encoding="utf-8")

    assert result.returncode == 0
    assert (
        "accepted iOS device launch rehearsal readiness exit code 2"
        in result.stdout
    )
    assert (
        "wrote services/backend/.local/ios-device-launch-rehearsal-readiness.json"
        in result.stdout
    )
    assert "wrote services/backend/.local/final-demo-launch-local.json" in result.stdout
    readiness_index = fake_uv_args.index("ios-device-launch-rehearsal-readiness")
    launch_index = fake_uv_args.index("final-demo-launch --mode local")
    assert readiness_index < launch_index
    assert "--output .local/ios-device-launch-rehearsal-readiness.json" in fake_uv_args
    assert "--output .local/final-demo-launch-local.json" in fake_uv_args


@pytest.mark.parametrize(
    ("target", "script_name", "accepted_message", "output_path"),
    PROVIDER_HANDOFF_SAFE_WRAPPERS,
)
def test_provider_handoff_safe_wrappers_accept_blocked_report_exit_code(
    script_repo: Path,
    target: str,
    script_name: str,
    accepted_message: str,
    output_path: str,
) -> None:
    _write_fake_uv(script_repo, exit_code=2)

    result = _run_script(script_repo, script_name)

    assert result.returncode == 0, target
    assert accepted_message in result.stdout
    assert output_path in result.stdout


@pytest.mark.parametrize(
    ("target", "script_name", "accepted_message", "output_path"),
    PROVIDER_HANDOFF_SAFE_WRAPPERS,
)
def test_provider_handoff_safe_wrappers_fail_unusable_exit_code(
    script_repo: Path,
    target: str,
    script_name: str,
    accepted_message: str,
    output_path: str,
) -> None:
    _write_fake_uv(script_repo, exit_code=1)

    result = _run_script(script_repo, script_name)

    assert result.returncode == 1, target
    assert "failed before writing a usable report: exit 1" in result.stderr
    assert accepted_message not in result.stdout
    assert output_path not in result.stdout


def test_write_ios_device_launch_rehearsal_fails_unusable_exit_code(
    script_repo: Path,
) -> None:
    _write_fake_make(script_repo, exit_code=1)
    _write_fake_uv(script_repo, exit_code=0)

    result = _run_script(script_repo, "write_ios_device_launch_rehearsal.sh")

    assert result.returncode == 1
    assert "final rehearsal failed before writing usable reports: exit 1" in result.stderr


def test_final_rehearsal_make_targets_dry_run_expected_order() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-rehearsal-local"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert "final-acceptance-local:" in makefile
    assert "ios-deploy-runbook-local:" in makefile
    assert "final-demo-launch-local:" in makefile
    assert "final-demo-launch: final-demo-launch-local" in makefile
    assert "final-rehearsal-local:" in makefile
    assert "services/backend/scripts/write_final_acceptance_local.sh" in makefile
    assert "services/backend/scripts/write_ios_deploy_runbook_local.sh" in makefile
    assert "--output .local/final-demo-launch-local.json" in makefile
    output = result.stdout
    assert "evaluate-3d" in output
    assert "evaluate-npc" in output
    assert "write_final_acceptance_local.sh" in output
    assert "write_final_acceptance_configured.sh" not in output
    assert "final-demo-launch --mode local" in output
    assert "write_ios_deploy_runbook_local.sh" in output
    assert "final-local-report-refresh-local:" in makefile
    assert "services/backend/scripts/write_final_local_report_refresh.sh" in makefile
    assert "write_final_local_report_refresh.sh" in output
    assert output.index("evaluate-3d") < output.index("evaluate-npc")
    assert output.index("evaluate-npc") < output.index("write_final_acceptance_local.sh")
    assert output.index("write_final_acceptance_local.sh") < output.index(
        "final-demo-launch --mode local"
    )
    assert output.index("final-demo-launch --mode local") < output.index(
        "write_ios_deploy_runbook_local.sh"
    )
    assert output.index("write_ios_deploy_runbook_local.sh") < output.index(
        "write_final_local_report_refresh.sh"
    )


def test_ios_device_launch_rehearsal_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "ios-device-launch-rehearsal"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert "ios-device-launch-rehearsal:" in makefile
    assert "services/backend/scripts/write_ios_device_launch_rehearsal.sh" in makefile
    assert "write_ios_device_launch_rehearsal.sh" in result.stdout


def test_final_acceptance_configured_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-acceptance-configured"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert (
        ".PHONY: final-acceptance-local final-acceptance-configured "
        "final-demo-launch final-demo-launch-local "
        "final-demo-launch-configured final-rehearsal-local"
    ) in makefile
    assert "final-acceptance-configured:" in makefile
    assert "services/backend/scripts/write_final_acceptance_configured.sh" in makefile
    assert "write_final_acceptance_configured.sh" in result.stdout


def test_final_local_report_refresh_make_target_dry_run_uses_cli() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-local-report-refresh"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert ".PHONY: final-local-report-refresh" in makefile
    assert "final-local-report-refresh:" in makefile
    assert "myth_forge_api.cli final-local-report-refresh" in result.stdout
    assert "--repo-root ../.." in result.stdout
    assert "--output .local/final-local-report-refresh.json" in result.stdout


def test_final_local_report_refresh_local_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-local-report-refresh-local"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert ".PHONY: final-local-report-refresh final-local-report-refresh-local" in makefile
    assert "final-local-report-refresh-local:" in makefile
    assert "write_final_local_report_refresh.sh" in result.stdout


def test_final_resource_fill_guide_make_target_dry_run_uses_cli() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-resource-fill-guide"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert ".PHONY: final-resource-fill-guide" in makefile
    assert "final-resource-fill-guide:" in makefile
    assert "myth_forge_api.cli final-resource-fill-guide" in result.stdout
    assert "--repo-root ../.." in result.stdout
    assert "--output .local/final-resource-fill-guide.json" in result.stdout
    assert "--markdown-output .local/final-resource-fill-guide.md" in result.stdout


def test_final_external_action_ledger_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-external-action-ledger"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert ".PHONY: final-external-action-ledger" in makefile
    assert "final-external-action-ledger:" in makefile
    assert "write_final_external_action_ledger.sh" in result.stdout


def test_final_external_action_ledger_wrapper_is_executable() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    wrapper = repo_root / "services/backend/scripts/write_final_external_action_ledger.sh"

    assert os.access(wrapper, os.X_OK)


def test_final_launch_closure_packet_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-launch-closure-packet"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert ".PHONY: final-launch-closure-packet" in makefile
    assert "final-launch-closure-packet:" in makefile
    assert "write_final_launch_closure_packet.sh" in result.stdout


def test_final_launch_closure_packet_wrapper_is_executable() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    wrapper = repo_root / "services/backend/scripts/write_final_launch_closure_packet.sh"

    assert os.access(wrapper, os.X_OK)


def test_mobile_deploy_preflight_evidence_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "mobile-deploy-preflight-evidence"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert ".PHONY: mobile-deploy-preflight-evidence" in makefile
    assert "mobile-deploy-preflight-evidence:" in makefile
    assert "write_mobile_deploy_preflight_evidence.sh" in result.stdout


def test_mobile_deploy_preflight_evidence_wrapper_is_executable() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    wrapper = (
        repo_root / "services/backend/scripts/write_mobile_deploy_preflight_evidence.sh"
    )

    assert os.access(wrapper, os.X_OK)


def test_final_showcase_readiness_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-showcase-readiness"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert ".PHONY: final-showcase-readiness" in makefile
    assert "final-showcase-readiness:" in makefile
    assert "write_final_showcase_readiness.sh" in result.stdout


def test_final_showcase_readiness_wrapper_is_executable() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    wrapper = repo_root / "services/backend/scripts/write_final_showcase_readiness.sh"

    assert os.access(wrapper, os.X_OK)


def test_mobile_xcode_build_evidence_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "mobile-xcode-build-evidence"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "write_mobile_xcode_build_evidence.sh" in result.stdout


def test_mobile_xcode_build_evidence_wrapper_is_executable() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    wrapper = repo_root / "services/backend/scripts/write_mobile_xcode_build_evidence.sh"

    assert os.access(wrapper, os.X_OK)


def test_ios_device_evidence_bundle_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "ios-device-evidence-bundle"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "write_ios_device_evidence_bundle.sh" in result.stdout


def test_ios_device_evidence_bundle_wrapper_is_executable() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    wrapper = repo_root / "services/backend/scripts/write_ios_device_evidence_bundle.sh"

    assert os.access(wrapper, os.X_OK)


def test_ios_device_launch_certificate_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "ios-device-launch-certificate"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "write_ios_device_launch_certificate.sh" in result.stdout


def test_ios_device_launch_certificate_wrapper_is_executable() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    wrapper = repo_root / "services/backend/scripts/write_ios_device_launch_certificate.sh"

    assert os.access(wrapper, os.X_OK)


def test_final_handoff_index_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-handoff-index"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "write_final_handoff_index.sh" in result.stdout


def test_final_handoff_index_wrapper_is_executable() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    wrapper = repo_root / "services/backend/scripts/write_final_handoff_index.sh"

    assert os.access(wrapper, os.X_OK)


def test_local_showcase_smoke_make_target_dry_run_uses_cli() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "local-showcase-smoke"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert ".PHONY: local-showcase-smoke" in makefile
    assert "local-showcase-smoke:" in makefile
    assert "myth_forge_api.cli local-showcase-smoke" in result.stdout
    assert "--output .local/local-showcase-smoke.json" in result.stdout


def test_final_configured_evidence_plan_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "final-configured-evidence-plan"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "write_final_configured_evidence_plan.sh" in result.stdout


def test_configured_live_evidence_bundle_make_target_dry_run_uses_wrapper() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", "configured-live-evidence-bundle"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "write_configured_live_evidence_bundle.sh" in result.stdout


@pytest.mark.parametrize(
    ("target", "script_name", "accepted_message", "output_path"),
    PROVIDER_HANDOFF_SAFE_WRAPPERS,
)
def test_provider_handoff_safe_wrapper_make_targets(
    target: str,
    script_name: str,
    accepted_message: str,
    output_path: str,
) -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        ["make", "-n", target],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert script_name in result.stdout
    wrapper = repo_root / "services/backend/scripts" / script_name
    assert os.access(wrapper, os.X_OK)
    wrapper_text = wrapper.read_text(encoding="utf-8")
    assert accepted_message.removesuffix(" 2") in wrapper_text
    assert output_path in wrapper_text


def _run_script(root: Path, script_name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", f"services/backend/scripts/{script_name}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        env={
            "PATH": f"{root / 'bin'}:{os.environ.get('PATH', '')}",
            "HOME": os.environ.get("HOME", ""),
        },
    )


def _write_fake_uv(root: Path, *, exit_code: int) -> None:
    fake_uv = root / "bin/uv"
    fake_uv.parent.mkdir(parents=True, exist_ok=True)
    fake_uv.write_text(
        "\n".join(
            [
                "#!/usr/bin/env sh",
                "printf '%s\\n' \"$*\" >> \"$PWD/.local/fake-uv-args.txt\"",
                f"exit {exit_code}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)


def _write_fake_make(root: Path, *, exit_code: int) -> None:
    fake_make = root / "bin/make"
    fake_make.parent.mkdir(parents=True, exist_ok=True)
    fake_make.write_text(
        "\n".join(
            [
                "#!/usr/bin/env sh",
                "mkdir -p services/backend/.local",
                "printf '%s\\n' \"$*\" >> services/backend/.local/fake-make-args.txt",
                f"exit {exit_code}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake_make.chmod(0o755)


@pytest.fixture
def script_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    source_root = Path(__file__).resolve().parents[3]
    shutil.copytree(source_root / "services/backend/scripts", root / "services/backend/scripts")
    (root / "services/backend").mkdir(parents=True, exist_ok=True)
    return root
