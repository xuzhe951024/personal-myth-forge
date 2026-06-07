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
                "printf '%s\\n' \"$*\" > \"$PWD/.local/fake-uv-args.txt\"",
                f"exit {exit_code}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)


@pytest.fixture
def script_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    source_root = Path(__file__).resolve().parents[3]
    shutil.copytree(source_root / "services/backend/scripts", root / "services/backend/scripts")
    (root / "services/backend").mkdir(parents=True, exist_ok=True)
    return root
