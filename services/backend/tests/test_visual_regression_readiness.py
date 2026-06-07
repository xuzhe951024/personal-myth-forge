import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from myth_forge_api.visual_regression_readiness import (
    build_visual_regression_readiness_report,
)


def test_visual_regression_readiness_missing_file_without_running_commands(
    tmp_path: Path,
) -> None:
    result = build_visual_regression_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["kind"] == "visual_regression_readiness_report"
    assert result.report["status"] == "missing"
    assert result.report["source_file"] == {
        "path": "services/backend/.local/visual-regression-local.json",
        "exists": False,
    }
    assert result.report["summary"] == {"passed": 0, "failed": 0}
    assert result.report["artifacts"] == []
    assert result.report["blockers"] == []
    assert "make visual-regression-local" in result.report["operator_actions"][0]
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["provider_calls"] is False
    assert result.report["safety"]["raw_media_in_report"] is False


def test_visual_regression_readiness_ready_from_saved_report(tmp_path: Path) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-07T12:00:00+00:00",
    )
    report_path = _write_visual_report(repo_root, status="passed", passed=1, failed=0)
    _set_mtime(report_path, "2026-06-07T12:05:00+00:00")

    result = build_visual_regression_readiness_report(repo_root=repo_root)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["summary"] == {"passed": 1, "failed": 0}
    assert result.report["artifacts"][0]["id"] == "p0.118_scene_load_proof"
    assert result.report["freshness"]["status"] == "fresh"
    assert result.report["operator_actions"] == []


def test_visual_regression_readiness_blocks_failed_report_and_redacts(
    tmp_path: Path,
) -> None:
    _write_visual_report(
        tmp_path,
        status="failed",
        passed=0,
        failed=1,
        artifact_status="failed",
        detail=(
            "Screenshot leaked Authorization=Bearer test-secret "
            "file:///Users/example/private.png local-capture://cap "
            "data:image/png;base64,abc123 checkout_url https://pay.example/abc"
        ),
    )

    result = build_visual_regression_readiness_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["blockers"][0]["classification"] == "visual_regression_failed"
    assert result.report["blockers"][0]["command"] == "make visual-regression-local"
    assert "rerun make visual-regression-local" in result.report["operator_actions"][0]
    assert "[redacted]" in report_text or "[withheld]" in report_text
    assert "test-secret" not in report_text
    assert "/Users/" not in report_text
    assert "file://" not in report_text
    assert "local-capture://" not in report_text
    assert "data:image" not in report_text
    assert "checkout_url" not in report_text
    assert "pay.example" not in report_text


def test_visual_regression_readiness_blocks_stale_report(tmp_path: Path) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-07T12:10:00+00:00",
    )
    report_path = _write_visual_report(repo_root, status="passed", passed=1, failed=0)
    _set_mtime(report_path, "2026-06-07T12:00:00+00:00")

    result = build_visual_regression_readiness_report(repo_root=repo_root)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["freshness"]["status"] == "stale"
    assert result.report["blockers"][0]["classification"] == "stale_report"
    assert "current git revision" in result.report["operator_actions"][0]


def test_visual_regression_readiness_blocks_unreadable_json(tmp_path: Path) -> None:
    path = _visual_report_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not-json", encoding="utf-8")

    result = build_visual_regression_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["blockers"][0]["classification"] == "unreadable_report"
    assert result.report["blockers"][0]["command"] == "make visual-regression-local"


def test_visual_regression_readiness_cli_writes_report(tmp_path: Path) -> None:
    _write_visual_report(tmp_path, status="passed", passed=1, failed=0)
    output = tmp_path / "visual-readiness.json"

    from myth_forge_api.cli import main

    exit_code = main(
        [
            "visual-regression-readiness",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["kind"] == "visual_regression_readiness_report"
    assert payload["status"] == "ready"


def test_visual_regression_makefile_exposes_local_report_target() -> None:
    makefile = (Path(__file__).resolve().parents[3] / "Makefile").read_text(
        encoding="utf-8"
    )

    assert "visual-regression-local:" in makefile
    assert "--output .local/visual-regression-local.json" in makefile
    assert "final-rehearsal-local: backend-evaluate-local visual-regression-local" in makefile


def _write_visual_report(
    repo_root: Path,
    *,
    status: str,
    passed: int,
    failed: int,
    artifact_status: str = "passed",
    detail: str = "",
) -> Path:
    artifact = {
        "id": "p0.118_scene_load_proof",
        "status": artifact_status,
        "html_path": "docs/superpowers/verification/p0.118-scene-load-proof.html",
        "png_path": "docs/superpowers/verification/assets/p0.118-scene-load-proof-390x844.png",
        "checks": {
            "html_exists": {"status": "passed"},
            "png_exists": {"status": "passed"},
            "unsafe_text": {
                "status": "failed" if detail else "passed",
                "matches": [detail] if detail else [],
            },
        },
    }
    report = {
        "kind": "visual_regression_report",
        "status": status,
        "summary": {"passed": passed, "failed": failed},
        "artifacts": [artifact],
    }
    path = _visual_report_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def _visual_report_path(repo_root: Path) -> Path:
    return repo_root / "services/backend/.local/visual-regression-local.json"


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
    subprocess.run(["git", "add", "README.md"], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_root,
        check=True,
        env=env,
        capture_output=True,
    )
    return repo_root


def _set_mtime(path: Path, iso_timestamp: str) -> None:
    epoch = datetime.fromisoformat(iso_timestamp).timestamp()
    os.utime(path, (epoch, epoch))
