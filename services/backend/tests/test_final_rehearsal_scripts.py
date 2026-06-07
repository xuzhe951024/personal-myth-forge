from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


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
    assert "services/backend/.local/ios-device-launch-rehearsal.json" in result.stdout
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
    assert "final-rehearsal-local:" in makefile
    assert "services/backend/scripts/write_final_acceptance_local.sh" in makefile
    assert "services/backend/scripts/write_ios_deploy_runbook_local.sh" in makefile
    assert "--output .local/final-demo-launch-local.json" in makefile
    output = result.stdout
    assert "evaluate-3d" in output
    assert "evaluate-npc" in output
    assert "write_final_acceptance_local.sh" in output
    assert "final-demo-launch" in output
    assert "write_ios_deploy_runbook_local.sh" in output
    assert output.index("evaluate-3d") < output.index("evaluate-npc")
    assert output.index("evaluate-npc") < output.index("write_final_acceptance_local.sh")
    assert output.index("write_final_acceptance_local.sh") < output.index("final-demo-launch")
    assert output.index("final-demo-launch") < output.index("write_ios_deploy_runbook_local.sh")


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
