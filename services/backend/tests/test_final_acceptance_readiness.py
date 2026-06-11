import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from myth_forge_api.final_acceptance_readiness import (
    build_final_acceptance_readiness_report,
)


def test_final_acceptance_readiness_missing_file_without_running_commands(
    tmp_path: Path,
) -> None:
    result = build_final_acceptance_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["kind"] == "final_acceptance_readiness_report"
    assert result.report["status"] == "missing"
    assert result.report["source_file"] == {
        "path": "services/backend/.local/final-acceptance-local.json",
        "exists": False,
    }
    assert result.report["summary"] == {
        "passed": 0,
        "blocked": 0,
        "failed": 0,
        "skipped": 0,
    }
    assert result.report["freshness"] == {
        "status": "unknown",
        "classification": "source_missing",
        "checked_against": "git_head",
        "source_modified_at": None,
        "current_revision": None,
        "current_revision_committed_at": None,
    }
    assert result.report["blockers"] == []
    assert result.report["operator_actions"] == [
        "run make final-acceptance-local to write services/backend/.local/final-acceptance-local.json"
    ]
    assert result.report["safety"] == {
        "commands_run": False,
        "provider_calls": False,
        "global_mutation": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
    }


def test_final_acceptance_readiness_marks_saved_report_fresh_against_git_head(
    tmp_path: Path,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-06T12:00:00+00:00",
    )
    report_path = _write_final_acceptance_report(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [
                {"id": "provider_handoff", "label": "Provider handoff", "status": "passed"},
            ],
        },
    )
    _set_mtime(report_path, "2026-06-06T12:05:00+00:00")

    result = build_final_acceptance_readiness_report(repo_root=repo_root)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["freshness"]["status"] == "fresh"
    assert result.report["freshness"]["classification"] == "fresh_report"
    assert result.report["freshness"]["current_revision"]


def test_final_acceptance_readiness_blocks_stale_saved_report_against_git_head(
    tmp_path: Path,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-06T12:10:00+00:00",
    )
    report_path = _write_final_acceptance_report(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [
                {"id": "provider_handoff", "label": "Provider handoff", "status": "passed"},
            ],
        },
    )
    _set_mtime(report_path, "2026-06-06T12:00:00+00:00")

    result = build_final_acceptance_readiness_report(repo_root=repo_root)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["freshness"]["status"] == "stale"
    assert result.report["freshness"]["classification"] == "stale_report"
    assert result.report["blockers"][0]["id"] == "final_acceptance_freshness"
    assert result.report["blockers"][0]["classification"] == "stale_report"
    assert result.report["operator_actions"][0] == (
        "rerun make final-acceptance-local to regenerate "
        "services/backend/.local/final-acceptance-local.json for the current product sources"
    )


def test_final_acceptance_readiness_ignores_newer_docs_only_commit(
    tmp_path: Path,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-06T12:00:00+00:00",
    )
    report_path = _write_final_acceptance_report(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "provider_handoff",
                    "label": "Provider handoff",
                    "status": "passed",
                },
            ],
        },
    )
    _set_mtime(report_path, "2026-06-06T12:05:00+00:00")
    _commit_fixture_file(
        repo_root,
        relative_path="docs/superpowers/plans/docs-only.md",
        content="docs only\n",
        committed_at="2026-06-06T12:10:00+00:00",
        message="docs only",
    )

    result = build_final_acceptance_readiness_report(repo_root=repo_root)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["freshness"]["status"] == "fresh"
    assert result.report["freshness"]["checked_against"] == "git_product_sources"


def test_final_acceptance_readiness_marks_freshness_unknown_without_git(
    tmp_path: Path,
) -> None:
    _write_final_acceptance_report(
        tmp_path,
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [
                {"id": "provider_handoff", "label": "Provider handoff", "status": "passed"},
            ],
        },
    )

    result = build_final_acceptance_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["freshness"]["status"] == "unknown"
    assert result.report["freshness"]["classification"] == "git_unavailable"


def test_final_acceptance_readiness_blocks_from_saved_report_without_unsafe_text(
    tmp_path: Path,
) -> None:
    _write_final_acceptance_report(
        tmp_path,
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 2, "failed": 0, "skipped": 0},
            "checks": [
                {"id": "provider_handoff", "label": "Provider handoff", "status": "passed"},
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_deploy_config",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stderr_tail": f"Missing DEVELOPMENT_TEAM in {tmp_path}/repo/private /Users/zhexu/private.",
                },
                {
                    "id": "mobile_xcode_build",
                    "label": "Xcode build gate",
                    "status": "blocked",
                    "classification": "blocked_by_apple_sdk_license",
                    "command": ["make", "mobile-xcode-build"],
                    "stderr_tail": "xcodebuild license blocked sk-secret checkout_url file:///tmp/private",
                },
            ],
        },
    )

    result = build_final_acceptance_readiness_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["summary"] == {
        "passed": 12,
        "blocked": 2,
        "failed": 0,
        "skipped": 0,
    }
    assert result.report["blockers"] == [
        {
            "id": "mobile_deploy_preflight",
            "label": "iOS deploy preflight",
            "status": "blocked",
            "classification": "blocked_by_local_ios_deploy_config",
            "command": "make mobile-deploy-preflight",
            "detail": "Missing DEVELOPMENT_TEAM in [repo-root]/repo/private [home]/private.",
        },
        {
            "id": "mobile_xcode_build",
            "label": "Xcode build gate",
            "status": "blocked",
            "classification": "blocked_by_apple_sdk_license",
            "command": "make mobile-xcode-build",
            "detail": "xcodebuild license blocked [redacted] [redacted] [redacted]",
        },
    ]
    assert result.report["operator_actions"] == [
        "provide iOS deploy config and rerun mobile deploy preflight",
        "resolve Xcode build gate outside the app",
    ]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-secret" not in report_text
    assert "checkout_url" not in report_text
    assert "file:///tmp" not in report_text


def test_final_acceptance_readiness_enriches_mobile_preflight_blocker_with_saved_next_action(
    tmp_path: Path,
) -> None:
    _write_final_acceptance_report(
        tmp_path,
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_deploy_config",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stderr_tail": "Missing DEVELOPMENT_TEAM in Deployment.local.xcconfig.",
                },
            ],
        },
    )
    _write_mobile_deploy_preflight_evidence(
        tmp_path,
        next_action={
            "id": "development_team",
            "label": "Apple Team ID",
            "status": "blocked",
            "command": "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
            "detail": "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable",
            "validation_command": "make mobile-deploy-preflight",
            "source": "first_blocker",
        },
    )

    result = build_final_acceptance_readiness_report(repo_root=tmp_path)

    blocker = result.report["blockers"][0]
    assert blocker["id"] == "mobile_deploy_preflight"
    assert blocker["next_action"] == {
        "id": "development_team",
        "label": "Apple Team ID",
        "status": "blocked",
        "command": "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
        "detail": "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable",
        "validation_command": "make mobile-deploy-preflight",
        "source": "first_blocker",
    }
    assert result.report["operator_actions"] == [
        (
            "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
            "rerun make mobile-deploy-preflight"
        )
    ]


def test_final_acceptance_readiness_ready_from_saved_report(tmp_path: Path) -> None:
    _write_final_acceptance_report(
        tmp_path,
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [
                {"id": "provider_handoff", "label": "Provider handoff", "status": "passed"},
                {"id": "demo_acceptance", "label": "Demo acceptance", "status": "passed"},
            ],
        },
    )

    result = build_final_acceptance_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["summary"] == {
        "passed": 14,
        "blocked": 0,
        "failed": 0,
        "skipped": 0,
    }
    assert result.report["blockers"] == []
    assert result.report["operator_actions"] == ["final acceptance is ready"]


def test_final_acceptance_readiness_blocks_malformed_file_safely(tmp_path: Path) -> None:
    report_path = tmp_path / "services/backend/.local/final-acceptance-local.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text("{not-json sk-secret /Users/zhexu/private", encoding="utf-8")

    result = build_final_acceptance_readiness_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["blockers"] == [
        {
            "id": "final_acceptance_file",
            "label": "Final acceptance file",
            "status": "failed",
            "classification": "unreadable_report",
            "command": "make final-acceptance-local",
            "detail": "Saved final acceptance report is not valid JSON.",
        }
    ]
    assert result.report["operator_actions"] == [
        "rerun make final-acceptance-local to regenerate services/backend/.local/final-acceptance-local.json"
    ]
    assert "sk-secret" not in report_text
    assert "/Users/" not in report_text


def _init_git_repo(tmp_path: Path, *, committed_at: str) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    subprocess.run(
        ["git", "init"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    (repo_root / "README.md").write_text("freshness fixture\n", encoding="utf-8")
    (repo_root / "Makefile").write_text(
        "backend-test:\n\tpytest\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", "README.md", "Makefile"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GIT_AUTHOR_DATE": committed_at,
            "GIT_COMMITTER_DATE": committed_at,
        }
    )
    subprocess.run(
        ["git", "commit", "-m", "fixture"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return repo_root


def _commit_fixture_file(
    repo_root: Path,
    *,
    relative_path: str,
    content: str,
    committed_at: str,
    message: str,
) -> None:
    path = repo_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", relative_path], cwd=repo_root, check=True)
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GIT_AUTHOR_DATE": committed_at,
            "GIT_COMMITTER_DATE": committed_at,
        }
    )
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )


def _set_mtime(path: Path, iso_timestamp: str) -> None:
    timestamp = datetime.fromisoformat(iso_timestamp).timestamp()
    os.utime(path, (timestamp, timestamp))


def _write_final_acceptance_report(repo_root: Path, report: dict[str, object]) -> Path:
    report_path = repo_root / "services/backend/.local/final-acceptance-local.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(json.dumps(report), encoding="utf-8")
    return report_path


def _write_mobile_deploy_preflight_evidence(
    repo_root: Path,
    *,
    next_action: dict[str, object],
) -> Path:
    report_path = (
        repo_root / "services/backend/.local/mobile-deploy-preflight-evidence.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "kind": "mobile_deploy_preflight_evidence_report",
                "status": "blocked",
                "next_action": next_action,
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
        ),
        encoding="utf-8",
    )
    return report_path
